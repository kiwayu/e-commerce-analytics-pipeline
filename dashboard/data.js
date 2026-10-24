window.DASHBOARD_DATA = {
 "as_of": "2026-10-24",
 "generated_at": "2026-10-24T09:59:39+00:00",
 "pipeline": {
  "last_run": "2026-10-24T10:59:17.943161+01:00",
  "raw_loaded_at": "2026-10-24T10:37:57.306294+01:00",
  "layers": [
   {
    "layer": "raw",
    "tables": [
     {
      "name": "raw_customers",
      "rows": 500
     },
     {
      "name": "raw_orders",
      "rows": 5000
     },
     {
      "name": "raw_shipments",
      "rows": 2413
     }
    ]
   },
   {
    "layer": "staging",
    "tables": [
     {
      "name": "stg_raw_customers",
      "rows": 500
     },
     {
      "name": "stg_raw_orders",
      "rows": 4896
     },
     {
      "name": "stg_raw_shipments",
      "rows": 2413
     }
    ]
   },
   {
    "layer": "intermediate",
    "tables": [
     {
      "name": "int_customer_order_metrics",
      "rows": 500
     },
     {
      "name": "int_order_shipment_combined",
      "rows": 4896
     }
    ]
   },
   {
    "layer": "marts",
    "tables": [
     {
      "name": "dim_customers",
      "rows": 500
     },
     {
      "name": "fact_orders",
      "rows": 4896
     },
     {
      "name": "revenue_daily",
      "rows": 91
     },
     {
      "name": "customer_segmentation",
      "rows": 500
     }
    ]
   }
  ],
  "dbt": {
   "models": 9,
   "tests": 112,
   "tests_passed": 112,
   "elapsed_seconds": 13.0
  }
 },
 "daily": [
  {
   "date_day": "2026-07-27",
   "total_orders": 64,
   "gross_revenue": 63394.57,
   "net_revenue": 41861.0,
   "average_order_value": 990.54015625,
   "fulfillment_rate": 0.59375,
   "cancellation_rate": 0.21875,
   "gross_revenue_7d_ma": 45938.685,
   "total_orders_7d_ma": 46.5
  },
  {
   "date_day": "2026-07-28",
   "total_orders": 59,
   "gross_revenue": 57878.52,
   "net_revenue": 33117.92,
   "average_order_value": 980.9918644067797,
   "fulfillment_rate": 0.5932203389830508,
   "cancellation_rate": 0.1864406779661017,
   "gross_revenue_7d_ma": 49918.63,
   "total_orders_7d_ma": 50.666666666666664
  },
  {
   "date_day": "2026-07-29",
   "total_orders": 66,
   "gross_revenue": 68335.77,
   "net_revenue": 42149.82,
   "average_order_value": 1035.3904545454545,
   "fulfillment_rate": 0.6060606060606061,
   "cancellation_rate": 0.13636363636363635,
   "gross_revenue_7d_ma": 54522.915,
   "total_orders_7d_ma": 54.5
  },
  {
   "date_day": "2026-07-30",
   "total_orders": 59,
   "gross_revenue": 58657.23,
   "net_revenue": 37525.96,
   "average_order_value": 994.1903389830509,
   "fulfillment_rate": 0.6440677966101694,
   "cancellation_rate": 0.288135593220339,
   "gross_revenue_7d_ma": 55349.778,
   "total_orders_7d_ma": 55.4
  },
  {
   "date_day": "2026-07-31",
   "total_orders": 44,
   "gross_revenue": 42483.62,
   "net_revenue": 24526.68,
   "average_order_value": 965.5368181818181,
   "fulfillment_rate": 0.5909090909090909,
   "cancellation_rate": 0.1590909090909091,
   "gross_revenue_7d_ma": 53205.418333333335,
   "total_orders_7d_ma": 53.5
  },
  {
   "date_day": "2026-08-01",
   "total_orders": 60,
   "gross_revenue": 62393.95,
   "net_revenue": 40997.12,
   "average_order_value": 1039.8991666666666,
   "fulfillment_rate": 0.6333333333333333,
   "cancellation_rate": 0.11666666666666667,
   "gross_revenue_7d_ma": 54518.065714285716,
   "total_orders_7d_ma": 54.42857142857143
  },
  {
   "date_day": "2026-08-02",
   "total_orders": 61,
   "gross_revenue": 52515.35,
   "net_revenue": 25636.57,
   "average_order_value": 860.9073770491804,
   "fulfillment_rate": 0.5573770491803278,
   "cancellation_rate": 0.2786885245901639,
   "gross_revenue_7d_ma": 57951.287142857145,
   "total_orders_7d_ma": 59.0
  },
  {
   "date_day": "2026-08-03",
   "total_orders": 49,
   "gross_revenue": 47294.75,
   "net_revenue": 33557.9,
   "average_order_value": 965.1989795918367,
   "fulfillment_rate": 0.673469387755102,
   "cancellation_rate": 0.1836734693877551,
   "gross_revenue_7d_ma": 55651.31285714286,
   "total_orders_7d_ma": 56.857142857142854
  },
  {
   "date_day": "2026-08-04",
   "total_orders": 50,
   "gross_revenue": 48148.84,
   "net_revenue": 29168.84,
   "average_order_value": 962.9768,
   "fulfillment_rate": 0.6,
   "cancellation_rate": 0.14,
   "gross_revenue_7d_ma": 54261.35857142857,
   "total_orders_7d_ma": 55.57142857142857
  },
  {
   "date_day": "2026-08-05",
   "total_orders": 67,
   "gross_revenue": 61901.42,
   "net_revenue": 35350.37,
   "average_order_value": 923.9017910447761,
   "fulfillment_rate": 0.6119402985074627,
   "cancellation_rate": 0.1791044776119403,
   "gross_revenue_7d_ma": 53342.165714285715,
   "total_orders_7d_ma": 55.714285714285715
  },
  {
   "date_day": "2026-08-06",
   "total_orders": 52,
   "gross_revenue": 48137.12,
   "net_revenue": 24504.05,
   "average_order_value": 925.7138461538461,
   "fulfillment_rate": 0.46153846153846156,
   "cancellation_rate": 0.21153846153846154,
   "gross_revenue_7d_ma": 51839.29285714286,
   "total_orders_7d_ma": 54.714285714285715
  },
  {
   "date_day": "2026-08-07",
   "total_orders": 49,
   "gross_revenue": 48317.16,
   "net_revenue": 30165.44,
   "average_order_value": 986.0644897959183,
   "fulfillment_rate": 0.5714285714285714,
   "cancellation_rate": 0.2857142857142857,
   "gross_revenue_7d_ma": 52672.65571428571,
   "total_orders_7d_ma": 55.42857142857143
  },
  {
   "date_day": "2026-08-08",
   "total_orders": 58,
   "gross_revenue": 53358.0,
   "net_revenue": 29111.26,
   "average_order_value": 919.9655172413793,
   "fulfillment_rate": 0.5344827586206896,
   "cancellation_rate": 0.1896551724137931,
   "gross_revenue_7d_ma": 51381.805714285714,
   "total_orders_7d_ma": 55.142857142857146
  },
  {
   "date_day": "2026-08-09",
   "total_orders": 47,
   "gross_revenue": 46052.62,
   "net_revenue": 33270.92,
   "average_order_value": 979.8429787234043,
   "fulfillment_rate": 0.6595744680851063,
   "cancellation_rate": 0.19148936170212766,
   "gross_revenue_7d_ma": 50458.55857142857,
   "total_orders_7d_ma": 53.142857142857146
  },
  {
   "date_day": "2026-08-10",
   "total_orders": 65,
   "gross_revenue": 53568.81,
   "net_revenue": 25768.2,
   "average_order_value": 824.1355384615384,
   "fulfillment_rate": 0.49230769230769234,
   "cancellation_rate": 0.3230769230769231,
   "gross_revenue_7d_ma": 51354.852857142854,
   "total_orders_7d_ma": 55.42857142857143
  },
  {
   "date_day": "2026-08-11",
   "total_orders": 60,
   "gross_revenue": 58804.05,
   "net_revenue": 36958.27,
   "average_order_value": 980.0675,
   "fulfillment_rate": 0.6,
   "cancellation_rate": 0.21666666666666667,
   "gross_revenue_7d_ma": 52877.025714285715,
   "total_orders_7d_ma": 56.857142857142854
  },
  {
   "date_day": "2026-08-12",
   "total_orders": 57,
   "gross_revenue": 55820.05,
   "net_revenue": 23534.0,
   "average_order_value": 979.2991228070175,
   "fulfillment_rate": 0.47368421052631576,
   "cancellation_rate": 0.22807017543859648,
   "gross_revenue_7d_ma": 52008.258571428574,
   "total_orders_7d_ma": 55.42857142857143
  },
  {
   "date_day": "2026-08-13",
   "total_orders": 54,
   "gross_revenue": 53007.46,
   "net_revenue": 31341.71,
   "average_order_value": 981.6196296296297,
   "fulfillment_rate": 0.5555555555555556,
   "cancellation_rate": 0.2037037037037037,
   "gross_revenue_7d_ma": 52704.02142857143,
   "total_orders_7d_ma": 55.714285714285715
  },
  {
   "date_day": "2026-08-14",
   "total_orders": 55,
   "gross_revenue": 57158.51,
   "net_revenue": 31182.24,
   "average_order_value": 1039.2456363636363,
   "fulfillment_rate": 0.5454545454545454,
   "cancellation_rate": 0.14545454545454545,
   "gross_revenue_7d_ma": 53967.07142857143,
   "total_orders_7d_ma": 56.57142857142857
  },
  {
   "date_day": "2026-08-15",
   "total_orders": 57,
   "gross_revenue": 54780.23,
   "net_revenue": 37325.0,
   "average_order_value": 961.0566666666666,
   "fulfillment_rate": 0.6842105263157895,
   "cancellation_rate": 0.19298245614035087,
   "gross_revenue_7d_ma": 54170.247142857144,
   "total_orders_7d_ma": 56.42857142857143
  },
  {
   "date_day": "2026-08-16",
   "total_orders": 42,
   "gross_revenue": 42416.1,
   "net_revenue": 22521.03,
   "average_order_value": 1009.9071428571428,
   "fulfillment_rate": 0.5,
   "cancellation_rate": 0.23809523809523808,
   "gross_revenue_7d_ma": 53650.74428571429,
   "total_orders_7d_ma": 55.714285714285715
  },
  {
   "date_day": "2026-08-17",
   "total_orders": 58,
   "gross_revenue": 45955.03,
   "net_revenue": 24712.99,
   "average_order_value": 792.3281034482759,
   "fulfillment_rate": 0.5689655172413793,
   "cancellation_rate": 0.22413793103448276,
   "gross_revenue_7d_ma": 52563.061428571425,
   "total_orders_7d_ma": 54.714285714285715
  },
  {
   "date_day": "2026-08-18",
   "total_orders": 57,
   "gross_revenue": 55269.9,
   "net_revenue": 28582.78,
   "average_order_value": 969.6473684210526,
   "fulfillment_rate": 0.5087719298245614,
   "cancellation_rate": 0.19298245614035087,
   "gross_revenue_7d_ma": 52058.182857142856,
   "total_orders_7d_ma": 54.285714285714285
  },
  {
   "date_day": "2026-08-19",
   "total_orders": 63,
   "gross_revenue": 63844.18,
   "net_revenue": 39046.37,
   "average_order_value": 1013.3996825396825,
   "fulfillment_rate": 0.6190476190476191,
   "cancellation_rate": 0.2222222222222222,
   "gross_revenue_7d_ma": 53204.48714285714,
   "total_orders_7d_ma": 55.142857142857146
  },
  {
   "date_day": "2026-08-20",
   "total_orders": 51,
   "gross_revenue": 53233.19,
   "net_revenue": 33746.17,
   "average_order_value": 1043.7880392156862,
   "fulfillment_rate": 0.6078431372549019,
   "cancellation_rate": 0.17647058823529413,
   "gross_revenue_7d_ma": 53236.73428571429,
   "total_orders_7d_ma": 54.714285714285715
  },
  {
   "date_day": "2026-08-21",
   "total_orders": 47,
   "gross_revenue": 45698.3,
   "net_revenue": 27281.05,
   "average_order_value": 972.304255319149,
   "fulfillment_rate": 0.5319148936170213,
   "cancellation_rate": 0.2553191489361702,
   "gross_revenue_7d_ma": 51599.561428571425,
   "total_orders_7d_ma": 53.57142857142857
  },
  {
   "date_day": "2026-08-22",
   "total_orders": 61,
   "gross_revenue": 56648.13,
   "net_revenue": 37851.36,
   "average_order_value": 928.657868852459,
   "fulfillment_rate": 0.5901639344262295,
   "cancellation_rate": 0.19672131147540983,
   "gross_revenue_7d_ma": 51866.404285714285,
   "total_orders_7d_ma": 54.142857142857146
  },
  {
   "date_day": "2026-08-23",
   "total_orders": 49,
   "gross_revenue": 45011.11,
   "net_revenue": 26588.74,
   "average_order_value": 918.5940816326531,
   "fulfillment_rate": 0.5306122448979592,
   "cancellation_rate": 0.22448979591836735,
   "gross_revenue_7d_ma": 52237.12,
   "total_orders_7d_ma": 55.142857142857146
  },
  {
   "date_day": "2026-08-24",
   "total_orders": 52,
   "gross_revenue": 50631.57,
   "net_revenue": 31767.25,
   "average_order_value": 973.6840384615384,
   "fulfillment_rate": 0.6153846153846154,
   "cancellation_rate": 0.25,
   "gross_revenue_7d_ma": 52905.19714285714,
   "total_orders_7d_ma": 54.285714285714285
  },
  {
   "date_day": "2026-08-25",
   "total_orders": 44,
   "gross_revenue": 48936.31,
   "net_revenue": 37820.41,
   "average_order_value": 1112.1888636363637,
   "fulfillment_rate": 0.7272727272727273,
   "cancellation_rate": 0.13636363636363635,
   "gross_revenue_7d_ma": 52000.39857142857,
   "total_orders_7d_ma": 52.42857142857143
  },
  {
   "date_day": "2026-08-26",
   "total_orders": 51,
   "gross_revenue": 47767.13,
   "net_revenue": 34079.28,
   "average_order_value": 936.6103921568628,
   "fulfillment_rate": 0.6862745098039216,
   "cancellation_rate": 0.19607843137254902,
   "gross_revenue_7d_ma": 49703.677142857145,
   "total_orders_7d_ma": 50.714285714285715
  },
  {
   "date_day": "2026-08-27",
   "total_orders": 46,
   "gross_revenue": 49944.65,
   "net_revenue": 28908.65,
   "average_order_value": 1085.753260869565,
   "fulfillment_rate": 0.5652173913043478,
   "cancellation_rate": 0.10869565217391304,
   "gross_revenue_7d_ma": 49233.885714285716,
   "total_orders_7d_ma": 50.0
  },
  {
   "date_day": "2026-08-28",
   "total_orders": 58,
   "gross_revenue": 55766.04,
   "net_revenue": 32433.35,
   "average_order_value": 961.4834482758621,
   "fulfillment_rate": 0.5862068965517241,
   "cancellation_rate": 0.2413793103448276,
   "gross_revenue_7d_ma": 50672.13428571429,
   "total_orders_7d_ma": 51.57142857142857
  },
  {
   "date_day": "2026-08-29",
   "total_orders": 62,
   "gross_revenue": 58649.84,
   "net_revenue": 31309.12,
   "average_order_value": 945.9651612903226,
   "fulfillment_rate": 0.4838709677419355,
   "cancellation_rate": 0.27419354838709675,
   "gross_revenue_7d_ma": 50958.09285714286,
   "total_orders_7d_ma": 51.714285714285715
  },
  {
   "date_day": "2026-08-30",
   "total_orders": 44,
   "gross_revenue": 39973.49,
   "net_revenue": 20666.63,
   "average_order_value": 908.488409090909,
   "fulfillment_rate": 0.6136363636363636,
   "cancellation_rate": 0.20454545454545456,
   "gross_revenue_7d_ma": 50238.432857142856,
   "total_orders_7d_ma": 51.0
  },
  {
   "date_day": "2026-08-31",
   "total_orders": 61,
   "gross_revenue": 63942.15,
   "net_revenue": 42597.5,
   "average_order_value": 1048.2319672131148,
   "fulfillment_rate": 0.6557377049180327,
   "cancellation_rate": 0.2459016393442623,
   "gross_revenue_7d_ma": 52139.944285714286,
   "total_orders_7d_ma": 52.285714285714285
  },
  {
   "date_day": "2026-09-01",
   "total_orders": 64,
   "gross_revenue": 58383.12,
   "net_revenue": 32635.75,
   "average_order_value": 912.23625,
   "fulfillment_rate": 0.546875,
   "cancellation_rate": 0.15625,
   "gross_revenue_7d_ma": 53489.48857142857,
   "total_orders_7d_ma": 55.142857142857146
  },
  {
   "date_day": "2026-09-02",
   "total_orders": 56,
   "gross_revenue": 57994.26,
   "net_revenue": 30218.28,
   "average_order_value": 1035.6117857142858,
   "fulfillment_rate": 0.5,
   "cancellation_rate": 0.21428571428571427,
   "gross_revenue_7d_ma": 54950.50714285715,
   "total_orders_7d_ma": 55.857142857142854
  },
  {
   "date_day": "2026-09-03",
   "total_orders": 51,
   "gross_revenue": 51162.71,
   "net_revenue": 30906.58,
   "average_order_value": 1003.1903921568628,
   "fulfillment_rate": 0.5490196078431373,
   "cancellation_rate": 0.1568627450980392,
   "gross_revenue_7d_ma": 55124.51571428571,
   "total_orders_7d_ma": 56.57142857142857
  },
  {
   "date_day": "2026-09-04",
   "total_orders": 58,
   "gross_revenue": 63219.06,
   "net_revenue": 46033.91,
   "average_order_value": 1089.9837931034483,
   "fulfillment_rate": 0.6724137931034483,
   "cancellation_rate": 0.10344827586206896,
   "gross_revenue_7d_ma": 56189.23285714286,
   "total_orders_7d_ma": 56.57142857142857
  },
  {
   "date_day": "2026-09-05",
   "total_orders": 62,
   "gross_revenue": 59912.16,
   "net_revenue": 25508.3,
   "average_order_value": 966.3251612903226,
   "fulfillment_rate": 0.46774193548387094,
   "cancellation_rate": 0.2903225806451613,
   "gross_revenue_7d_ma": 56369.56428571429,
   "total_orders_7d_ma": 56.57142857142857
  },
  {
   "date_day": "2026-09-06",
   "total_orders": 53,
   "gross_revenue": 45756.08,
   "net_revenue": 21666.19,
   "average_order_value": 863.3222641509434,
   "fulfillment_rate": 0.5094339622641509,
   "cancellation_rate": 0.22641509433962265,
   "gross_revenue_7d_ma": 57195.64857142857,
   "total_orders_7d_ma": 57.857142857142854
  },
  {
   "date_day": "2026-09-07",
   "total_orders": 54,
   "gross_revenue": 57830.73,
   "net_revenue": 34793.18,
   "average_order_value": 1070.9394444444445,
   "fulfillment_rate": 0.5555555555555556,
   "cancellation_rate": 0.3333333333333333,
   "gross_revenue_7d_ma": 56322.58857142857,
   "total_orders_7d_ma": 56.857142857142854
  },
  {
   "date_day": "2026-09-08",
   "total_orders": 52,
   "gross_revenue": 44267.25,
   "net_revenue": 35648.95,
   "average_order_value": 851.2932692307693,
   "fulfillment_rate": 0.7307692307692307,
   "cancellation_rate": 0.15384615384615385,
   "gross_revenue_7d_ma": 54306.03571428572,
   "total_orders_7d_ma": 55.142857142857146
  },
  {
   "date_day": "2026-09-09",
   "total_orders": 57,
   "gross_revenue": 59348.12,
   "net_revenue": 24294.57,
   "average_order_value": 1041.1950877192983,
   "fulfillment_rate": 0.43859649122807015,
   "cancellation_rate": 0.21052631578947367,
   "gross_revenue_7d_ma": 54499.444285714286,
   "total_orders_7d_ma": 55.285714285714285
  },
  {
   "date_day": "2026-09-10",
   "total_orders": 48,
   "gross_revenue": 51546.59,
   "net_revenue": 30878.84,
   "average_order_value": 1073.8872916666667,
   "fulfillment_rate": 0.6041666666666666,
   "cancellation_rate": 0.25,
   "gross_revenue_7d_ma": 54554.28428571429,
   "total_orders_7d_ma": 54.857142857142854
  },
  {
   "date_day": "2026-09-11",
   "total_orders": 48,
   "gross_revenue": 53321.18,
   "net_revenue": 31420.76,
   "average_order_value": 1110.8579166666666,
   "fulfillment_rate": 0.5416666666666666,
   "cancellation_rate": 0.25,
   "gross_revenue_7d_ma": 53140.30142857143,
   "total_orders_7d_ma": 53.42857142857143
  },
  {
   "date_day": "2026-09-12",
   "total_orders": 48,
   "gross_revenue": 45030.61,
   "net_revenue": 22500.13,
   "average_order_value": 938.1377083333333,
   "fulfillment_rate": 0.5208333333333334,
   "cancellation_rate": 0.20833333333333334,
   "gross_revenue_7d_ma": 51014.36571428571,
   "total_orders_7d_ma": 51.42857142857143
  },
  {
   "date_day": "2026-09-13",
   "total_orders": 45,
   "gross_revenue": 43781.88,
   "net_revenue": 17831.9,
   "average_order_value": 972.9306666666666,
   "fulfillment_rate": 0.5333333333333333,
   "cancellation_rate": 0.2222222222222222,
   "gross_revenue_7d_ma": 50732.33714285714,
   "total_orders_7d_ma": 50.285714285714285
  },
  {
   "date_day": "2026-09-14",
   "total_orders": 46,
   "gross_revenue": 52232.1,
   "net_revenue": 31128.15,
   "average_order_value": 1135.4804347826087,
   "fulfillment_rate": 0.6739130434782609,
   "cancellation_rate": 0.15217391304347827,
   "gross_revenue_7d_ma": 49932.532857142854,
   "total_orders_7d_ma": 49.142857142857146
  },
  {
   "date_day": "2026-09-15",
   "total_orders": 61,
   "gross_revenue": 54614.88,
   "net_revenue": 21077.13,
   "average_order_value": 895.3259016393442,
   "fulfillment_rate": 0.4426229508196721,
   "cancellation_rate": 0.21311475409836064,
   "gross_revenue_7d_ma": 51410.76571428571,
   "total_orders_7d_ma": 50.42857142857143
  },
  {
   "date_day": "2026-09-16",
   "total_orders": 62,
   "gross_revenue": 61154.8,
   "net_revenue": 39522.16,
   "average_order_value": 986.3677419354839,
   "fulfillment_rate": 0.6290322580645161,
   "cancellation_rate": 0.20967741935483872,
   "gross_revenue_7d_ma": 51668.862857142856,
   "total_orders_7d_ma": 51.142857142857146
  },
  {
   "date_day": "2026-09-17",
   "total_orders": 50,
   "gross_revenue": 49968.99,
   "net_revenue": 22659.47,
   "average_order_value": 999.3798,
   "fulfillment_rate": 0.46,
   "cancellation_rate": 0.32,
   "gross_revenue_7d_ma": 51443.491428571426,
   "total_orders_7d_ma": 51.42857142857143
  },
  {
   "date_day": "2026-09-18",
   "total_orders": 67,
   "gross_revenue": 55315.91,
   "net_revenue": 28875.87,
   "average_order_value": 825.6105970149254,
   "fulfillment_rate": 0.5373134328358209,
   "cancellation_rate": 0.22388059701492538,
   "gross_revenue_7d_ma": 51728.45285714286,
   "total_orders_7d_ma": 54.142857142857146
  },
  {
   "date_day": "2026-09-19",
   "total_orders": 55,
   "gross_revenue": 47336.52,
   "net_revenue": 24901.21,
   "average_order_value": 860.664,
   "fulfillment_rate": 0.5636363636363636,
   "cancellation_rate": 0.21818181818181817,
   "gross_revenue_7d_ma": 52057.86857142857,
   "total_orders_7d_ma": 55.142857142857146
  },
  {
   "date_day": "2026-09-20",
   "total_orders": 56,
   "gross_revenue": 59989.12,
   "net_revenue": 38736.16,
   "average_order_value": 1071.2342857142858,
   "fulfillment_rate": 0.6428571428571429,
   "cancellation_rate": 0.19642857142857142,
   "gross_revenue_7d_ma": 54373.188571428575,
   "total_orders_7d_ma": 56.714285714285715
  },
  {
   "date_day": "2026-09-21",
   "total_orders": 59,
   "gross_revenue": 59242.99,
   "net_revenue": 27105.59,
   "average_order_value": 1004.1184745762712,
   "fulfillment_rate": 0.5423728813559322,
   "cancellation_rate": 0.2542372881355932,
   "gross_revenue_7d_ma": 55374.74428571429,
   "total_orders_7d_ma": 58.57142857142857
  },
  {
   "date_day": "2026-09-22",
   "total_orders": 54,
   "gross_revenue": 52305.78,
   "net_revenue": 34864.82,
   "average_order_value": 968.6255555555556,
   "fulfillment_rate": 0.7037037037037037,
   "cancellation_rate": 0.12962962962962962,
   "gross_revenue_7d_ma": 55044.87285714286,
   "total_orders_7d_ma": 57.57142857142857
  },
  {
   "date_day": "2026-09-23",
   "total_orders": 51,
   "gross_revenue": 46179.68,
   "net_revenue": 24149.23,
   "average_order_value": 905.4839215686275,
   "fulfillment_rate": 0.5882352941176471,
   "cancellation_rate": 0.21568627450980393,
   "gross_revenue_7d_ma": 52905.57,
   "total_orders_7d_ma": 56.0
  },
  {
   "date_day": "2026-09-24",
   "total_orders": 51,
   "gross_revenue": 46031.6,
   "net_revenue": 24334.93,
   "average_order_value": 902.5803921568628,
   "fulfillment_rate": 0.5294117647058824,
   "cancellation_rate": 0.27450980392156865,
   "gross_revenue_7d_ma": 52343.08571428571,
   "total_orders_7d_ma": 56.142857142857146
  },
  {
   "date_day": "2026-09-25",
   "total_orders": 50,
   "gross_revenue": 57651.56,
   "net_revenue": 37461.28,
   "average_order_value": 1153.0312,
   "fulfillment_rate": 0.64,
   "cancellation_rate": 0.18,
   "gross_revenue_7d_ma": 52676.75,
   "total_orders_7d_ma": 53.714285714285715
  },
  {
   "date_day": "2026-09-26",
   "total_orders": 63,
   "gross_revenue": 59319.53,
   "net_revenue": 32524.9,
   "average_order_value": 941.5798412698413,
   "fulfillment_rate": 0.5873015873015873,
   "cancellation_rate": 0.19047619047619047,
   "gross_revenue_7d_ma": 54388.60857142857,
   "total_orders_7d_ma": 54.857142857142854
  },
  {
   "date_day": "2026-09-27",
   "total_orders": 51,
   "gross_revenue": 51322.63,
   "net_revenue": 28097.35,
   "average_order_value": 1006.3260784313726,
   "fulfillment_rate": 0.5294117647058824,
   "cancellation_rate": 0.23529411764705882,
   "gross_revenue_7d_ma": 53150.53857142857,
   "total_orders_7d_ma": 54.142857142857146
  },
  {
   "date_day": "2026-09-28",
   "total_orders": 45,
   "gross_revenue": 39768.28,
   "net_revenue": 17333.11,
   "average_order_value": 883.7395555555555,
   "fulfillment_rate": 0.4666666666666667,
   "cancellation_rate": 0.37777777777777777,
   "gross_revenue_7d_ma": 50368.43714285714,
   "total_orders_7d_ma": 52.142857142857146
  },
  {
   "date_day": "2026-09-29",
   "total_orders": 55,
   "gross_revenue": 47880.67,
   "net_revenue": 27677.29,
   "average_order_value": 870.5576363636363,
   "fulfillment_rate": 0.5454545454545454,
   "cancellation_rate": 0.16363636363636364,
   "gross_revenue_7d_ma": 49736.27857142857,
   "total_orders_7d_ma": 52.285714285714285
  },
  {
   "date_day": "2026-09-30",
   "total_orders": 55,
   "gross_revenue": 52405.64,
   "net_revenue": 23613.54,
   "average_order_value": 952.8298181818182,
   "fulfillment_rate": 0.45454545454545453,
   "cancellation_rate": 0.32727272727272727,
   "gross_revenue_7d_ma": 50625.70142857143,
   "total_orders_7d_ma": 52.857142857142854
  },
  {
   "date_day": "2026-10-01",
   "total_orders": 57,
   "gross_revenue": 51362.66,
   "net_revenue": 27493.19,
   "average_order_value": 901.099298245614,
   "fulfillment_rate": 0.5614035087719298,
   "cancellation_rate": 0.19298245614035087,
   "gross_revenue_7d_ma": 51387.28142857143,
   "total_orders_7d_ma": 53.714285714285715
  },
  {
   "date_day": "2026-10-02",
   "total_orders": 44,
   "gross_revenue": 38521.24,
   "net_revenue": 17601.29,
   "average_order_value": 875.4827272727273,
   "fulfillment_rate": 0.4772727272727273,
   "cancellation_rate": 0.20454545454545456,
   "gross_revenue_7d_ma": 48654.37857142857,
   "total_orders_7d_ma": 52.857142857142854
  },
  {
   "date_day": "2026-10-03",
   "total_orders": 49,
   "gross_revenue": 46888.7,
   "net_revenue": 26139.35,
   "average_order_value": 956.9122448979592,
   "fulfillment_rate": 0.4897959183673469,
   "cancellation_rate": 0.2857142857142857,
   "gross_revenue_7d_ma": 46878.54571428571,
   "total_orders_7d_ma": 50.857142857142854
  },
  {
   "date_day": "2026-10-04",
   "total_orders": 49,
   "gross_revenue": 45204.98,
   "net_revenue": 25118.87,
   "average_order_value": 922.5506122448979,
   "fulfillment_rate": 0.5306122448979592,
   "cancellation_rate": 0.22448979591836735,
   "gross_revenue_7d_ma": 46004.595714285715,
   "total_orders_7d_ma": 50.57142857142857
  },
  {
   "date_day": "2026-10-05",
   "total_orders": 58,
   "gross_revenue": 47366.26,
   "net_revenue": 30191.75,
   "average_order_value": 816.6596551724137,
   "fulfillment_rate": 0.603448275862069,
   "cancellation_rate": 0.1724137931034483,
   "gross_revenue_7d_ma": 47090.02142857143,
   "total_orders_7d_ma": 52.42857142857143
  },
  {
   "date_day": "2026-10-06",
   "total_orders": 48,
   "gross_revenue": 44767.04,
   "net_revenue": 30059.98,
   "average_order_value": 932.6466666666666,
   "fulfillment_rate": 0.625,
   "cancellation_rate": 0.14583333333333334,
   "gross_revenue_7d_ma": 46645.217142857146,
   "total_orders_7d_ma": 51.42857142857143
  },
  {
   "date_day": "2026-10-07",
   "total_orders": 67,
   "gross_revenue": 67124.54,
   "net_revenue": 40605.46,
   "average_order_value": 1001.8588059701492,
   "fulfillment_rate": 0.5671641791044776,
   "cancellation_rate": 0.208955223880597,
   "gross_revenue_7d_ma": 48747.91714285714,
   "total_orders_7d_ma": 53.142857142857146
  },
  {
   "date_day": "2026-10-08",
   "total_orders": 27,
   "gross_revenue": 21391.54,
   "net_revenue": 11451.02,
   "average_order_value": 792.2792592592592,
   "fulfillment_rate": 0.5185185185185185,
   "cancellation_rate": 0.18518518518518517,
   "gross_revenue_7d_ma": 44466.328571428574,
   "total_orders_7d_ma": 48.857142857142854
  },
  {
   "date_day": "2026-10-09",
   "total_orders": 61,
   "gross_revenue": 56520.89,
   "net_revenue": 36167.19,
   "average_order_value": 926.5719672131147,
   "fulfillment_rate": 0.7049180327868853,
   "cancellation_rate": 0.09836065573770492,
   "gross_revenue_7d_ma": 47037.70714285714,
   "total_orders_7d_ma": 51.285714285714285
  },
  {
   "date_day": "2026-10-10",
   "total_orders": 62,
   "gross_revenue": 62665.39,
   "net_revenue": 23941.73,
   "average_order_value": 1010.7320967741936,
   "fulfillment_rate": 0.43548387096774194,
   "cancellation_rate": 0.2903225806451613,
   "gross_revenue_7d_ma": 49291.52,
   "total_orders_7d_ma": 53.142857142857146
  },
  {
   "date_day": "2026-10-11",
   "total_orders": 56,
   "gross_revenue": 55726.43,
   "net_revenue": 32096.33,
   "average_order_value": 995.1148214285714,
   "fulfillment_rate": 0.5178571428571429,
   "cancellation_rate": 0.21428571428571427,
   "gross_revenue_7d_ma": 50794.584285714285,
   "total_orders_7d_ma": 54.142857142857146
  },
  {
   "date_day": "2026-10-12",
   "total_orders": 60,
   "gross_revenue": 58200.22,
   "net_revenue": 25536.91,
   "average_order_value": 970.0036666666666,
   "fulfillment_rate": 0.43333333333333335,
   "cancellation_rate": 0.31666666666666665,
   "gross_revenue_7d_ma": 52342.29285714286,
   "total_orders_7d_ma": 54.42857142857143
  },
  {
   "date_day": "2026-10-13",
   "total_orders": 43,
   "gross_revenue": 46023.34,
   "net_revenue": 25961.14,
   "average_order_value": 1070.3102325581394,
   "fulfillment_rate": 0.5116279069767442,
   "cancellation_rate": 0.2558139534883721,
   "gross_revenue_7d_ma": 52521.764285714286,
   "total_orders_7d_ma": 53.714285714285715
  },
  {
   "date_day": "2026-10-14",
   "total_orders": 51,
   "gross_revenue": 40409.71,
   "net_revenue": 24873.62,
   "average_order_value": 792.3472549019608,
   "fulfillment_rate": 0.6470588235294118,
   "cancellation_rate": 0.13725490196078433,
   "gross_revenue_7d_ma": 48705.36,
   "total_orders_7d_ma": 51.42857142857143
  },
  {
   "date_day": "2026-10-15",
   "total_orders": 58,
   "gross_revenue": 58469.66,
   "net_revenue": 32161.76,
   "average_order_value": 1008.0975862068966,
   "fulfillment_rate": 0.5517241379310345,
   "cancellation_rate": 0.3103448275862069,
   "gross_revenue_7d_ma": 54002.23428571429,
   "total_orders_7d_ma": 55.857142857142854
  },
  {
   "date_day": "2026-10-16",
   "total_orders": 49,
   "gross_revenue": 46850.09,
   "net_revenue": 36173.22,
   "average_order_value": 956.1242857142857,
   "fulfillment_rate": 0.7755102040816326,
   "cancellation_rate": 0.10204081632653061,
   "gross_revenue_7d_ma": 52620.69142857143,
   "total_orders_7d_ma": 54.142857142857146
  },
  {
   "date_day": "2026-10-17",
   "total_orders": 71,
   "gross_revenue": 75436.76,
   "net_revenue": 38966.63,
   "average_order_value": 1062.4895774647887,
   "fulfillment_rate": 0.5211267605633803,
   "cancellation_rate": 0.23943661971830985,
   "gross_revenue_7d_ma": 54445.172857142854,
   "total_orders_7d_ma": 55.42857142857143
  },
  {
   "date_day": "2026-10-18",
   "total_orders": 66,
   "gross_revenue": 65506.72,
   "net_revenue": 46969.51,
   "average_order_value": 992.5260606060606,
   "fulfillment_rate": 0.7121212121212122,
   "cancellation_rate": 0.15151515151515152,
   "gross_revenue_7d_ma": 55842.357142857145,
   "total_orders_7d_ma": 56.857142857142854
  },
  {
   "date_day": "2026-10-19",
   "total_orders": 52,
   "gross_revenue": 44668.37,
   "net_revenue": 24868.01,
   "average_order_value": 859.0071153846154,
   "fulfillment_rate": 0.5576923076923077,
   "cancellation_rate": 0.25,
   "gross_revenue_7d_ma": 53909.235714285714,
   "total_orders_7d_ma": 55.714285714285715
  },
  {
   "date_day": "2026-10-20",
   "total_orders": 52,
   "gross_revenue": 53694.78,
   "net_revenue": 32126.97,
   "average_order_value": 1032.591923076923,
   "fulfillment_rate": 0.5192307692307693,
   "cancellation_rate": 0.15384615384615385,
   "gross_revenue_7d_ma": 55005.15571428571,
   "total_orders_7d_ma": 57.0
  },
  {
   "date_day": "2026-10-21",
   "total_orders": 53,
   "gross_revenue": 52114.44,
   "net_revenue": 33753.03,
   "average_order_value": 983.2913207547169,
   "fulfillment_rate": 0.6037735849056604,
   "cancellation_rate": 0.1509433962264151,
   "gross_revenue_7d_ma": 56677.26,
   "total_orders_7d_ma": 57.285714285714285
  },
  {
   "date_day": "2026-10-22",
   "total_orders": 45,
   "gross_revenue": 50694.98,
   "net_revenue": 31383.77,
   "average_order_value": 1126.555111111111,
   "fulfillment_rate": 0.6,
   "cancellation_rate": 0.2,
   "gross_revenue_7d_ma": 55566.59142857143,
   "total_orders_7d_ma": 55.42857142857143
  },
  {
   "date_day": "2026-10-23",
   "total_orders": 58,
   "gross_revenue": 51998.64,
   "net_revenue": 32696.41,
   "average_order_value": 896.528275862069,
   "fulfillment_rate": 0.6206896551724138,
   "cancellation_rate": 0.13793103448275862,
   "gross_revenue_7d_ma": 56302.09857142857,
   "total_orders_7d_ma": 56.714285714285715
  },
  {
   "date_day": "2026-10-24",
   "total_orders": 25,
   "gross_revenue": 24595.62,
   "net_revenue": 19144.36,
   "average_order_value": 983.8248,
   "fulfillment_rate": 0.68,
   "cancellation_rate": 0.08,
   "gross_revenue_7d_ma": 49039.078571428574,
   "total_orders_7d_ma": 50.142857142857146
  }
 ],
 "windows": {
  "7": {
   "metrics": {
    "current": {
     "orders": 351,
     "revenue": 343273.55,
     "aov": 977.9873219373219,
     "fulfillment_rate": 0.6125356125356125,
     "customers": 254
    },
    "previous": {
     "orders": 388,
     "revenue": 381116.21,
     "aov": 982.2582731958763,
     "fulfillment_rate": 0.5592783505154639,
     "customers": 270
    }
   },
   "status": [
    {
     "label": "delivered",
     "orders": 161,
     "revenue": 165454.21
    },
    {
     "label": "shipped",
     "orders": 54,
     "revenue": 55487.85
    },
    {
     "label": "processing",
     "orders": 40,
     "revenue": 34507.14
    },
    {
     "label": "pending",
     "orders": 38,
     "revenue": 37307.01
    },
    {
     "label": "refunded",
     "orders": 30,
     "revenue": 28723.8
    },
    {
     "label": "cancelled",
     "orders": 28,
     "revenue": 21793.54
    }
   ],
   "segments": [
    {
     "label": "loyal_customer",
     "orders": 329,
     "revenue": 322107.09,
     "customers": 234
    },
    {
     "label": "potential_loyalist",
     "orders": 12,
     "revenue": 12790.92,
     "customers": 12
    },
    {
     "label": "vip",
     "orders": 10,
     "revenue": 8375.54,
     "customers": 8
    }
   ],
   "countries": [
    {
     "label": "US",
     "orders": 114,
     "revenue": 113336.84,
     "aov": 994.1828070175438
    },
    {
     "label": "FR",
     "orders": 49,
     "revenue": 57064.7,
     "aov": 1164.5857142857142
    },
    {
     "label": "AU",
     "orders": 53,
     "revenue": 49267.24,
     "aov": 929.5705660377358
    },
    {
     "label": "DE",
     "orders": 51,
     "revenue": 45926.0,
     "aov": 900.5098039215686
    },
    {
     "label": "CA",
     "orders": 49,
     "revenue": 43088.13,
     "aov": 879.3495918367347
    },
    {
     "label": "GB",
     "orders": 35,
     "revenue": 34590.64,
     "aov": 988.304
    }
   ],
   "carriers": [
    {
     "label": "FedEx",
     "shipments": 44,
     "on_time_rate": 0.45454545454545453,
     "avg_days": 3.8636363636363638
    },
    {
     "label": "UPS",
     "shipments": 36,
     "on_time_rate": 0.3333333333333333,
     "avg_days": 4.222222222222222
    },
    {
     "label": "USPS",
     "shipments": 29,
     "on_time_rate": 0.5862068965517241,
     "avg_days": 3.896551724137931
    },
    {
     "label": "DHL",
     "shipments": 28,
     "on_time_rate": 0.5,
     "avg_days": 3.9285714285714284
    }
   ],
   "payment": [
    {
     "label": "credit_card",
     "orders": 150,
     "revenue": 147574.19
    },
    {
     "label": "apple_pay",
     "orders": 74,
     "revenue": 72807.19
    },
    {
     "label": "paypal",
     "orders": 66,
     "revenue": 68851.87
    },
    {
     "label": "bank_transfer",
     "orders": 61,
     "revenue": 54040.3
    }
   ]
  },
  "30": {
   "metrics": {
    "current": {
     "orders": 1580,
     "revenue": 1514551.31,
     "aov": 958.5767784810126,
     "fulfillment_rate": 0.5658227848101266,
     "customers": 470
    },
    "previous": {
     "orders": 1630,
     "revenue": 1591969.42,
     "aov": 976.6683558282209,
     "fulfillment_rate": 0.5674846625766872,
     "customers": 487
    }
   },
   "status": [
    {
     "label": "delivered",
     "orders": 710,
     "revenue": 693500.32
    },
    {
     "label": "shipped",
     "orders": 184,
     "revenue": 178688.65
    },
    {
     "label": "pending",
     "orders": 180,
     "revenue": 169535.96
    },
    {
     "label": "processing",
     "orders": 177,
     "revenue": 177802.57
    },
    {
     "label": "cancelled",
     "orders": 175,
     "revenue": 161038.54
    },
    {
     "label": "refunded",
     "orders": 154,
     "revenue": 133985.27
    }
   ],
   "segments": [
    {
     "label": "loyal_customer",
     "orders": 1479,
     "revenue": 1422142.68,
     "customers": 429
    },
    {
     "label": "vip",
     "orders": 54,
     "revenue": 49998.97,
     "customers": 13
    },
    {
     "label": "potential_loyalist",
     "orders": 47,
     "revenue": 42409.66,
     "customers": 28
    }
   ],
   "countries": [
    {
     "label": "US",
     "orders": 505,
     "revenue": 470188.06,
     "aov": 931.0654653465347
    },
    {
     "label": "AU",
     "orders": 250,
     "revenue": 241268.93,
     "aov": 965.07572
    },
    {
     "label": "DE",
     "orders": 221,
     "revenue": 209026.85,
     "aov": 945.8228506787331
    },
    {
     "label": "FR",
     "orders": 204,
     "revenue": 206025.84,
     "aov": 1009.9305882352941
    },
    {
     "label": "CA",
     "orders": 214,
     "revenue": 201455.54,
     "aov": 941.3810280373832
    },
    {
     "label": "GB",
     "orders": 186,
     "revenue": 186586.09,
     "aov": 1003.1510215053763
    }
   ],
   "carriers": [
    {
     "label": "DHL",
     "shipments": 152,
     "on_time_rate": 0.47368421052631576,
     "avg_days": 4.019736842105263
    },
    {
     "label": "FedEx",
     "shipments": 152,
     "on_time_rate": 0.5460526315789473,
     "avg_days": 3.7828947368421053
    },
    {
     "label": "UPS",
     "shipments": 145,
     "on_time_rate": 0.4413793103448276,
     "avg_days": 4.055172413793104
    },
    {
     "label": "USPS",
     "shipments": 143,
     "on_time_rate": 0.5174825174825175,
     "avg_days": 3.909090909090909
    }
   ],
   "payment": [
    {
     "label": "credit_card",
     "orders": 660,
     "revenue": 609380.46
    },
    {
     "label": "apple_pay",
     "orders": 310,
     "revenue": 302687.14
    },
    {
     "label": "paypal",
     "orders": 309,
     "revenue": 314162.31
    },
    {
     "label": "bank_transfer",
     "orders": 301,
     "revenue": 288321.4
    }
   ]
  },
  "90": {
   "metrics": {
    "current": {
     "orders": 4867,
     "revenue": 4706172.58,
     "aov": 966.9555331826588,
     "fulfillment_rate": 0.5720156153688104,
     "customers": 500
    },
    "previous": {
     "orders": 29,
     "revenue": 28482.8,
     "aov": 982.1655172413793,
     "fulfillment_rate": 0.4482758620689655,
     "customers": 29
    }
   },
   "status": [
    {
     "label": "delivered",
     "orders": 2220,
     "revenue": 2184351.81
    },
    {
     "label": "shipped",
     "orders": 564,
     "revenue": 536495.17
    },
    {
     "label": "cancelled",
     "orders": 545,
     "revenue": 534361.0
    },
    {
     "label": "processing",
     "orders": 539,
     "revenue": 527732.76
    },
    {
     "label": "pending",
     "orders": 520,
     "revenue": 487089.9
    },
    {
     "label": "refunded",
     "orders": 479,
     "revenue": 436141.94
    }
   ],
   "segments": [
    {
     "label": "loyal_customer",
     "orders": 4409,
     "revenue": 4265201.54,
     "customers": 435
    },
    {
     "label": "at_risk",
     "orders": 160,
     "revenue": 165995.14,
     "customers": 23
    },
    {
     "label": "vip",
     "orders": 170,
     "revenue": 160317.06,
     "customers": 13
    },
    {
     "label": "potential_loyalist",
     "orders": 128,
     "revenue": 114658.84,
     "customers": 29
    }
   ],
   "countries": [
    {
     "label": "US",
     "orders": 1521,
     "revenue": 1461659.23,
     "aov": 960.9856870479947
    },
    {
     "label": "DE",
     "orders": 743,
     "revenue": 728660.48,
     "aov": 980.7005114401077
    },
    {
     "label": "AU",
     "orders": 744,
     "revenue": 708619.28,
     "aov": 952.4452688172044
    },
    {
     "label": "FR",
     "orders": 656,
     "revenue": 640944.72,
     "aov": 977.0498780487804
    },
    {
     "label": "CA",
     "orders": 613,
     "revenue": 600287.0,
     "aov": 979.2610114192496
    },
    {
     "label": "GB",
     "orders": 590,
     "revenue": 566001.87,
     "aov": 959.3252033898306
    }
   ],
   "carriers": [
    {
     "label": "FedEx",
     "shipments": 480,
     "on_time_rate": 0.5208333333333334,
     "avg_days": 3.9291666666666667
    },
    {
     "label": "UPS",
     "shipments": 480,
     "on_time_rate": 0.48333333333333334,
     "avg_days": 3.9895833333333335
    },
    {
     "label": "USPS",
     "shipments": 473,
     "on_time_rate": 0.5052854122621564,
     "avg_days": 3.9429175475687104
    },
    {
     "label": "DHL",
     "shipments": 455,
     "on_time_rate": 0.4835164835164835,
     "avg_days": 4.041758241758242
    }
   ],
   "payment": [
    {
     "label": "credit_card",
     "orders": 1988,
     "revenue": 1898209.66
    },
    {
     "label": "paypal",
     "orders": 978,
     "revenue": 979450.3
    },
    {
     "label": "bank_transfer",
     "orders": 955,
     "revenue": 912482.91
    },
    {
     "label": "apple_pay",
     "orders": 946,
     "revenue": 916029.71
    }
   ]
  }
 }
};
