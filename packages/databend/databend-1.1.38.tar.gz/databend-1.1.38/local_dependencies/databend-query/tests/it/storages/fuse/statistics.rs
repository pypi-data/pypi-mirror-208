//  Copyright 2021 Datafuse Labs.
//
//  Licensed under the Apache License, Version 2.0 (the "License");
//  you may not use this file except in compliance with the License.
//  You may obtain a copy of the License at
//
//      http://www.apache.org/licenses/LICENSE-2.0
//
//  Unless required by applicable law or agreed to in writing, software
//  distributed under the License is distributed on an "AS IS" BASIS,
//  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
//  See the License for the specific language governing permissions and
//  limitations under the License.

use std::collections::HashMap;
use std::sync::Arc;

use common_base::base::tokio;
use common_expression::type_check::check;
use common_expression::types::number::Int32Type;
use common_expression::types::number::NumberScalar;
use common_expression::types::DataType;
use common_expression::types::NumberDataType;
use common_expression::types::StringType;
use common_expression::BlockThresholds;
use common_expression::Column;
use common_expression::DataBlock;
use common_expression::DataField;
use common_expression::DataSchemaRefExt;
use common_expression::FromData;
use common_expression::FunctionContext;
use common_expression::RawExpr;
use common_expression::Scalar;
use common_expression::TableDataType;
use common_expression::TableField;
use common_expression::TableSchema;
use common_functions::aggregates::eval_aggr;
use common_functions::BUILTIN_FUNCTIONS;
use common_sql::evaluator::BlockOperator;
use common_storages_fuse::statistics::reducers::reduce_block_metas;
use common_storages_fuse::statistics::Trim;
use common_storages_fuse::statistics::STATS_REPLACEMENT_CHAR;
use common_storages_fuse::statistics::STATS_STRING_PREFIX_LEN;
use common_storages_fuse::FuseStorageFormat;
use databend_query::storages::fuse::io::TableMetaLocationGenerator;
use databend_query::storages::fuse::statistics::gen_columns_statistics;
use databend_query::storages::fuse::statistics::reducers;
use databend_query::storages::fuse::statistics::ClusterStatsGenerator;
use databend_query::storages::fuse::statistics::StatisticsAccumulator;
use databend_query::test_kits::block_writer::BlockWriter;
use databend_query::test_kits::table_test_fixture::TestFixture;
use opendal::Operator;
use rand::Rng;
use storages_common_table_meta::meta::BlockMeta;
use storages_common_table_meta::meta::ClusterStatistics;
use storages_common_table_meta::meta::ColumnStatistics;
use storages_common_table_meta::meta::Compression;
use storages_common_table_meta::meta::Statistics;

#[test]
fn test_ft_stats_block_stats() -> common_exception::Result<()> {
    let schema = Arc::new(TableSchema::new(vec![
        TableField::new("a", TableDataType::Number(NumberDataType::Int32)),
        TableField::new("b", TableDataType::String),
    ]));
    let block = DataBlock::new_from_columns(vec![
        Int32Type::from_data(vec![1, 2, 3]),
        StringType::from_data(vec!["aa", "aa", "bb"]),
    ]);

    let r = gen_columns_statistics(&block, None, &schema)?;
    assert_eq!(2, r.len());
    let col_stats = r.get(&0).unwrap();
    assert_eq!(col_stats.min, Scalar::Number(NumberScalar::Int32(1)));
    assert_eq!(col_stats.max, Scalar::Number(NumberScalar::Int32(3)));
    assert_eq!(col_stats.distinct_of_values, Some(3));
    let col_stats = r.get(&1).unwrap();
    assert_eq!(col_stats.min, Scalar::String(b"aa".to_vec()));
    assert_eq!(col_stats.max, Scalar::String(b"bb".to_vec()));
    assert_eq!(col_stats.distinct_of_values, Some(2));
    Ok(())
}

#[test]
fn test_ft_stats_block_stats_with_column_distinct_count() -> common_exception::Result<()> {
    let schema = Arc::new(TableSchema::new(vec![
        TableField::new("a", TableDataType::Number(NumberDataType::Int32)),
        TableField::new("b", TableDataType::String),
    ]));

    let block = DataBlock::new_from_columns(vec![
        Int32Type::from_data(vec![1, 2, 3]),
        StringType::from_data(vec!["aa", "aa", "bb"]),
    ]);
    let mut column_distinct_count = HashMap::new();
    column_distinct_count.insert(0, 3);
    column_distinct_count.insert(1, 2);
    let r = gen_columns_statistics(&block, Some(column_distinct_count), &schema)?;
    assert_eq!(2, r.len());
    let col_stats = r.get(&0).unwrap();
    assert_eq!(col_stats.min, Scalar::Number(NumberScalar::Int32(1)));
    assert_eq!(col_stats.max, Scalar::Number(NumberScalar::Int32(3)));
    assert_eq!(col_stats.distinct_of_values, Some(3));
    let col_stats = r.get(&1).unwrap();
    assert_eq!(col_stats.min, Scalar::String(b"aa".to_vec()));
    assert_eq!(col_stats.max, Scalar::String(b"bb".to_vec()));
    assert_eq!(col_stats.distinct_of_values, Some(2));
    Ok(())
}

#[test]
fn test_ft_tuple_stats_block_stats() -> common_exception::Result<()> {
    let schema = Arc::new(TableSchema::new(vec![TableField::new(
        "a",
        TableDataType::Tuple {
            fields_name: vec!["a11".to_string(), "a12".to_string()],
            fields_type: vec![
                TableDataType::Number(NumberDataType::Int32),
                TableDataType::Number(NumberDataType::Int32),
            ],
        },
    )]));

    let inner_columns = vec![
        Int32Type::from_data(vec![1, 2, 3]),
        Int32Type::from_data(vec![4, 5, 6]),
    ];
    let column = Column::Tuple(inner_columns);

    let block = DataBlock::new_from_columns(vec![column]);

    let r = gen_columns_statistics(&block, None, &schema)?;
    assert_eq!(2, r.len());
    let col0_stats = r.get(&0).unwrap();
    assert_eq!(col0_stats.min, Scalar::Number(NumberScalar::Int32(1)));
    assert_eq!(col0_stats.max, Scalar::Number(NumberScalar::Int32(3)));

    let col1_stats = r.get(&1).unwrap();
    assert_eq!(col1_stats.min, Scalar::Number(NumberScalar::Int32(4)));
    assert_eq!(col1_stats.max, Scalar::Number(NumberScalar::Int32(6)));
    Ok(())
}

#[test]
fn test_ft_stats_col_stats_reduce() -> common_exception::Result<()> {
    let num_of_blocks = 10;
    let rows_per_block = 3;
    let val_start_with = 1;

    let (schema, blocks) =
        TestFixture::gen_sample_blocks_ex(num_of_blocks, rows_per_block, val_start_with);
    let col_stats = blocks
        .iter()
        .map(|b| gen_columns_statistics(&b.clone().unwrap(), None, &schema))
        .collect::<common_exception::Result<Vec<_>>>()?;
    let r = reducers::reduce_block_statistics(&col_stats);
    assert!(r.is_ok());
    let r = r.unwrap();
    assert_eq!(3, r.len());
    let col0_stats = r.get(&0).unwrap();
    assert_eq!(
        col0_stats.min,
        Scalar::Number(NumberScalar::Int32(val_start_with))
    );
    assert_eq!(
        col0_stats.max,
        Scalar::Number(NumberScalar::Int32(num_of_blocks as i32))
    );

    let col1_stats = r.get(&1).unwrap();
    assert_eq!(
        col1_stats.min,
        Scalar::Number(NumberScalar::Int32(val_start_with * 2))
    );

    assert_eq!(
        col1_stats.max,
        Scalar::Number(NumberScalar::Int32((num_of_blocks * 2) as i32))
    );
    let col2_stats = r.get(&2).unwrap();
    assert_eq!(
        col2_stats.min,
        Scalar::Number(NumberScalar::Int32(val_start_with * 3))
    );
    assert_eq!(
        col2_stats.max,
        Scalar::Number(NumberScalar::Int32((num_of_blocks * 3) as i32))
    );
    Ok(())
}

#[test]
fn test_reduce_block_statistics_in_memory_size() -> common_exception::Result<()> {
    let iter = |mut idx| {
        std::iter::from_fn(move || {
            idx += 1;
            Some((idx, ColumnStatistics {
                min: Scalar::Null,
                max: Scalar::Null,
                null_count: 1,
                in_memory_size: 1,
                distinct_of_values: Some(1),
            }))
        })
    };

    let num_of_cols = 100;
    // combine two statistics
    let col_stats_left = HashMap::from_iter(iter(0).take(num_of_cols));
    let col_stats_right = HashMap::from_iter(iter(0).take(num_of_cols));
    let r = reducers::reduce_block_statistics(&[col_stats_left, col_stats_right])?;
    assert_eq!(num_of_cols, r.len());
    // there should be 100 columns in the result
    for idx in 1..=100 {
        let col_stats = r.get(&idx);
        assert!(col_stats.is_some());
        let col_stats = col_stats.unwrap();
        // for each column, the reduced value of in_memory_size should be 1 + 1
        assert_eq!(col_stats.in_memory_size, 2);
        // for each column, the reduced value of null_count should be 1 + 1
        assert_eq!(col_stats.null_count, 2);
    }
    Ok(())
}

#[tokio::test(flavor = "multi_thread")]
async fn test_accumulator() -> common_exception::Result<()> {
    let (schema, blocks) = TestFixture::gen_sample_blocks(10, 1);
    let mut stats_acc = StatisticsAccumulator::default();

    let operator = Operator::new(opendal::services::Memory::default())?.finish();
    let loc_generator = TableMetaLocationGenerator::with_prefix("/".to_owned());
    for item in blocks {
        let block = item?;
        let col_stats = gen_columns_statistics(&block, None, &schema)?;
        let block_writer = BlockWriter::new(&operator, &loc_generator);
        let (block_meta, _index_meta) = block_writer
            .write(FuseStorageFormat::Parquet, &schema, block, col_stats, None)
            .await?;
        stats_acc.add_with_block_meta(block_meta);
    }

    assert_eq!(10, stats_acc.blocks_statistics.len());
    assert!(stats_acc.index_size > 0);
    Ok(())
}

#[tokio::test(flavor = "multi_thread")]
async fn test_ft_cluster_stats_with_stats() -> common_exception::Result<()> {
    let schema = DataSchemaRefExt::create(vec![DataField::new(
        "a",
        DataType::Number(NumberDataType::Int32),
    )]);

    let columns = vec![Int32Type::from_data(vec![1i32, 2, 3])];

    let blocks = DataBlock::new_from_columns(columns);
    let origin = Some(ClusterStatistics {
        cluster_key_id: 0,
        min: vec![Scalar::Number(NumberScalar::Int32(1))],
        max: vec![Scalar::Number(NumberScalar::Int32(5))],
        level: 0,
        pages: None,
    });

    let block_compactor = BlockThresholds::new(1_000_000, 800_000, 100 * 1024 * 1024);
    let stats_gen = ClusterStatsGenerator::new(
        0,
        vec![0],
        0,
        None,
        0,
        block_compactor,
        vec![],
        vec![],
        FunctionContext::default(),
    );
    let stats = stats_gen.gen_with_origin_stats(&blocks, origin.clone())?;
    assert!(stats.is_some());
    let stats = stats.unwrap();
    assert_eq!(vec![Scalar::Number(NumberScalar::Int32(1))], stats.min);
    assert_eq!(vec![Scalar::Number(NumberScalar::Int32(3))], stats.max);

    // add expression executor.
    let expr = RawExpr::FunctionCall {
        span: None,
        name: "plus".to_string(),
        params: vec![],
        args: vec![
            RawExpr::ColumnRef {
                span: None,
                id: 0usize,
                data_type: schema.field(0).data_type().clone(),
                display_name: schema.field(0).name().clone(),
            },
            RawExpr::Constant {
                span: None,
                scalar: Scalar::Number(NumberScalar::UInt64(1)),
            },
        ],
    };
    let expr = check(&expr, &BUILTIN_FUNCTIONS).unwrap();

    let operators = vec![BlockOperator::Map { exprs: vec![expr] }];

    let stats_gen = ClusterStatsGenerator::new(
        0,
        vec![1],
        0,
        None,
        0,
        block_compactor,
        operators,
        vec![],
        FunctionContext::default(),
    );
    let stats = stats_gen.gen_with_origin_stats(&blocks, origin.clone())?;
    assert!(stats.is_some());
    let stats = stats.unwrap();
    assert_eq!(vec![Scalar::Number(NumberScalar::Int64(2))], stats.min);
    assert_eq!(vec![Scalar::Number(NumberScalar::Int64(4))], stats.max);

    // different cluster_key_id.
    let stats_gen = ClusterStatsGenerator::new(
        1,
        vec![0],
        0,
        None,
        0,
        block_compactor,
        vec![],
        vec![],
        FunctionContext::default(),
    );
    let stats = stats_gen.gen_with_origin_stats(&blocks, origin)?;
    assert!(stats.is_none());

    Ok(())
}

#[test]
fn test_ft_stats_block_stats_string_columns_trimming() -> common_exception::Result<()> {
    let suite = || -> common_exception::Result<()> {
        // prepare random strings
        // 100 string, length ranges from 0 to 100 (chars)
        let mut rand_strings: Vec<String> = vec![];
        for _ in 0..100 {
            let mut rnd = rand::thread_rng();
            let rand_string: String = rand::thread_rng()
                .sample_iter::<char, _>(rand::distributions::Standard)
                .take(rnd.gen_range(0..1000))
                .collect();

            rand_strings.push(rand_string);
        }

        let min_expr = rand_strings.iter().min().unwrap();
        let max_expr = rand_strings.iter().max().unwrap();

        let data_value_min = Scalar::String(min_expr.clone().into_bytes());
        let data_value_max = Scalar::String(max_expr.clone().into_bytes());

        let trimmed_min = data_value_min.clone().trim_min();
        let trimmed_max = data_value_max.clone().trim_max();

        let meaningless_to_collect_max = is_degenerated_case(max_expr.as_str());

        if meaningless_to_collect_max {
            assert!(trimmed_max.is_none());
        } else {
            assert!(trimmed_max.is_some());
            let trimmed = trimmed_max.unwrap().as_string().unwrap().clone();
            assert!(char_len(&trimmed) <= STATS_STRING_PREFIX_LEN);
            assert!(Scalar::String(trimmed) >= data_value_max)
        }

        {
            assert!(trimmed_min.is_some());
            let trimmed = trimmed_min.unwrap().as_string().unwrap().clone();
            assert!(char_len(&trimmed) <= STATS_STRING_PREFIX_LEN);
            assert!(Scalar::String(trimmed) <= data_value_min);
        }
        Ok(())
    };

    // let runs = 0..1000;  // use this setting at home
    let runs = 0..100;
    for _ in runs {
        suite()?
    }
    Ok(())
}

#[test]
fn test_ft_stats_block_stats_string_columns_trimming_using_eval() -> common_exception::Result<()> {
    // verifies (randomly) the following assumptions:
    //
    // https://github.com/datafuselabs/databend/issues/7829
    // > ...
    // > in a way that preserves the property of min/max statistics:
    // > the trimmed max should be larger than the non-trimmed one, and the trimmed min
    // > should be lesser than the non-trimmed one.

    let suite = || -> common_exception::Result<()> {
        // prepare random strings
        // 100 string, length ranges from 0 to 100 (chars)
        let mut rand_strings: Vec<String> = vec![];
        let rows = 100;
        for _ in 0..rows {
            let mut rnd = rand::thread_rng();
            let rand_string: String = rand::thread_rng()
                .sample_iter::<char, _>(rand::distributions::Standard)
                .take(rnd.gen_range(0..1000))
                .collect();

            rand_strings.push(rand_string);
        }

        let schema = Arc::new(TableSchema::new(vec![TableField::new(
            "a",
            TableDataType::String,
        )]));

        // build test data block, which has only on column, of String type
        let data_col = StringType::from_data(
            rand_strings
                .iter()
                .map(|s| s.as_str())
                .collect::<Vec<&str>>(),
        );
        let block = DataBlock::new_from_columns(vec![data_col.clone()]);

        let min_col = eval_aggr("min", vec![], &[data_col.clone()], rows)?;
        let max_col = eval_aggr("max", vec![], &[data_col], rows)?;

        let min_expr = min_col.0.index(0).unwrap();
        let max_expr = max_col.0.index(0).unwrap();

        // generate the statistics of column
        let stats_of_columns = gen_columns_statistics(&block, None, &schema).unwrap();

        // check if the max value (untrimmed) is in degenerated condition:
        // - the length of string value is larger or equal than STRING_PREFIX_LEN
        // - AND the string has a prefix of length STRING_PREFIX_LEN, for all the char C in prefix,
        //   C > REPLACEMENT_CHAR; which means we can not replace any of them.
        let string_max_expr = String::from_utf8(max_expr.as_string().unwrap().to_vec()).unwrap();
        let meaningless_to_collect_max = is_degenerated_case(string_max_expr.as_str());

        if meaningless_to_collect_max {
            // no stats will be collected
            assert!(stats_of_columns.get(&0).is_none())
        } else {
            // Finally:
            // check that, trimmed "col_stats.max" always large than or equal to the untrimmed "max_expr"
            let col_stats = stats_of_columns.get(&0).unwrap();
            assert!(
                col_stats.max >= max_expr.to_owned(),
                "left [{}]\nright [{}]",
                col_stats.max,
                max_expr
            );
            // check that, trimmed "col_stats.min" always less than or equal to the untrimmed "mn_expr"
            assert!(
                col_stats.min <= min_expr.to_owned(),
                "left [{}]\nright [{}]",
                col_stats.min,
                min_expr
            );
        }
        Ok(())
    };

    // let runs = 0..1000;  // use this at home

    let runs = 0..100;
    for _ in runs {
        suite()?
    }
    Ok(())
}

fn is_degenerated_case(value: &str) -> bool {
    // check if the value (untrimmed) is in degenerated condition:
    // - the length of string value is larger or equal than STRING_PREFIX_LEN
    // - AND the string has a prefix of length STRING_PREFIX_LEN, for all the char C in prefix,
    //   C > REPLACEMENT_CHAR; which means we can not replace any of them.
    let larger_than_prefix_len = value.chars().count() > STATS_STRING_PREFIX_LEN;
    let prefixed_with_irreplaceable_chars = value
        .chars()
        .take(STATS_STRING_PREFIX_LEN)
        .all(|c| c >= STATS_REPLACEMENT_CHAR);

    larger_than_prefix_len && prefixed_with_irreplaceable_chars
}

fn char_len(value: &[u8]) -> usize {
    String::from_utf8(value.to_vec())
        .unwrap()
        .as_str()
        .chars()
        .count()
}

#[test]
fn test_reduce_block_meta() -> common_exception::Result<()> {
    // case 1: empty input should return the default statistics
    let block_metas: Vec<BlockMeta> = vec![];
    let reduced = reduce_block_metas(&block_metas, BlockThresholds::default())?;
    assert_eq!(Statistics::default(), reduced);

    // case 2: accumulated variants of size index should be as expected
    // reduction of ColumnStatistics, ClusterStatistics already covered by other cases
    let mut rng = rand::thread_rng();
    let size = 100_u64;
    let location = ("".to_owned(), 0);
    let mut blocks = vec![];
    let mut acc_row_count = 0;
    let mut acc_block_size = 0;
    let mut acc_file_size = 0;
    let mut acc_bloom_filter_index_size = 0;
    for _ in 0..size {
        let row_count = rng.gen::<u64>() / size;
        let block_size = rng.gen::<u64>() / size;
        let file_size = rng.gen::<u64>() / size;
        let bloom_filter_index_size = rng.gen::<u64>() / size;
        acc_row_count += row_count;
        acc_block_size += block_size;
        acc_file_size += file_size;
        acc_bloom_filter_index_size += bloom_filter_index_size;
        let block_meta = BlockMeta::new(
            row_count,
            block_size,
            file_size,
            HashMap::new(),
            HashMap::new(),
            None,
            location.clone(),
            None,
            bloom_filter_index_size,
            Compression::Lz4Raw,
        );
        blocks.push(block_meta);
    }

    let stats = reduce_block_metas(&blocks, BlockThresholds::default())?;

    assert_eq!(acc_row_count, stats.row_count);
    assert_eq!(acc_block_size, stats.uncompressed_byte_size);
    assert_eq!(acc_file_size, stats.compressed_byte_size);
    assert_eq!(acc_bloom_filter_index_size, stats.index_size);

    Ok(())
}
