window.DASHBOARD_DATA = {
 "as_of": "2026-10-24",
 "generated_at": "2026-10-24T09:42:28+00:00",
 "pipeline": {
  "last_run": "2026-10-24T10:42:27.849838+01:00",
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
   "tests": 107,
   "tests_passed": 107,
   "elapsed_seconds": 13.2
  }
 },
 "daily": [
  {
   "date_day": "2026-07-27",
   "total_orders": 64,
   "gross_revenue": 68268.65,
   "net_revenue": 46195.54,
   "average_order_value": 1066.69765625,
   "fulfillment_rate": 0.59375,
   "cancellation_rate": 0.21875,
   "gross_revenue_7d_ma": 49423.605,
   "total_orders_7d_ma": 46.5
  },
  {
   "date_day": "2026-07-28",
   "total_orders": 59,
   "gross_revenue": 58215.04,
   "net_revenue": 31663.4,
   "average_order_value": 986.695593220339,
   "fulfillment_rate": 0.5932203389830508,
   "cancellation_rate": 0.1864406779661017,
   "gross_revenue_7d_ma": 52354.083333333336,
   "total_orders_7d_ma": 50.666666666666664
  },
  {
   "date_day": "2026-07-29",
   "total_orders": 66,
   "gross_revenue": 74199.2,
   "net_revenue": 45445.0,
   "average_order_value": 1124.230303030303,
   "fulfillment_rate": 0.6060606060606061,
   "cancellation_rate": 0.13636363636363635,
   "gross_revenue_7d_ma": 57815.3625,
   "total_orders_7d_ma": 54.5
  },
  {
   "date_day": "2026-07-30",
   "total_orders": 59,
   "gross_revenue": 61831.38,
   "net_revenue": 40268.88,
   "average_order_value": 1047.9894915254238,
   "fulfillment_rate": 0.6440677966101694,
   "cancellation_rate": 0.288135593220339,
   "gross_revenue_7d_ma": 58618.566,
   "total_orders_7d_ma": 55.4
  },
  {
   "date_day": "2026-07-31",
   "total_orders": 44,
   "gross_revenue": 43503.06,
   "net_revenue": 26583.64,
   "average_order_value": 988.7059090909091,
   "fulfillment_rate": 0.5909090909090909,
   "cancellation_rate": 0.1590909090909091,
   "gross_revenue_7d_ma": 56099.315,
   "total_orders_7d_ma": 53.5
  },
  {
   "date_day": "2026-08-01",
   "total_orders": 60,
   "gross_revenue": 65010.29,
   "net_revenue": 43117.04,
   "average_order_value": 1083.5048333333334,
   "fulfillment_rate": 0.6333333333333333,
   "cancellation_rate": 0.11666666666666667,
   "gross_revenue_7d_ma": 57372.311428571425,
   "total_orders_7d_ma": 54.42857142857143
  },
  {
   "date_day": "2026-08-02",
   "total_orders": 61,
   "gross_revenue": 55270.72,
   "net_revenue": 28864.24,
   "average_order_value": 906.0773770491803,
   "fulfillment_rate": 0.5573770491803278,
   "cancellation_rate": 0.2786885245901639,
   "gross_revenue_7d_ma": 60899.76285714286,
   "total_orders_7d_ma": 59.0
  },
  {
   "date_day": "2026-08-03",
   "total_orders": 49,
   "gross_revenue": 51846.28,
   "net_revenue": 36099.68,
   "average_order_value": 1058.0873469387755,
   "fulfillment_rate": 0.673469387755102,
   "cancellation_rate": 0.1836734693877551,
   "gross_revenue_7d_ma": 58553.71,
   "total_orders_7d_ma": 56.857142857142854
  },
  {
   "date_day": "2026-08-04",
   "total_orders": 50,
   "gross_revenue": 51907.04,
   "net_revenue": 30967.57,
   "average_order_value": 1038.1408,
   "fulfillment_rate": 0.6,
   "cancellation_rate": 0.14,
   "gross_revenue_7d_ma": 57652.567142857144,
   "total_orders_7d_ma": 55.57142857142857
  },
  {
   "date_day": "2026-08-05",
   "total_orders": 67,
   "gross_revenue": 63633.73,
   "net_revenue": 37021.61,
   "average_order_value": 949.7571641791045,
   "fulfillment_rate": 0.6119402985074627,
   "cancellation_rate": 0.1791044776119403,
   "gross_revenue_7d_ma": 56143.21428571428,
   "total_orders_7d_ma": 55.714285714285715
  },
  {
   "date_day": "2026-08-06",
   "total_orders": 52,
   "gross_revenue": 49223.07,
   "net_revenue": 23666.01,
   "average_order_value": 946.5975,
   "fulfillment_rate": 0.46153846153846156,
   "cancellation_rate": 0.21153846153846154,
   "gross_revenue_7d_ma": 54342.02714285714,
   "total_orders_7d_ma": 54.714285714285715
  },
  {
   "date_day": "2026-08-07",
   "total_orders": 49,
   "gross_revenue": 51278.52,
   "net_revenue": 29549.59,
   "average_order_value": 1046.5004081632653,
   "fulfillment_rate": 0.5714285714285714,
   "cancellation_rate": 0.2857142857142857,
   "gross_revenue_7d_ma": 55452.80714285714,
   "total_orders_7d_ma": 55.42857142857143
  },
  {
   "date_day": "2026-08-08",
   "total_orders": 58,
   "gross_revenue": 55353.64,
   "net_revenue": 30317.62,
   "average_order_value": 954.3731034482759,
   "fulfillment_rate": 0.5344827586206896,
   "cancellation_rate": 0.1896551724137931,
   "gross_revenue_7d_ma": 54073.28571428572,
   "total_orders_7d_ma": 55.142857142857146
  },
  {
   "date_day": "2026-08-09",
   "total_orders": 47,
   "gross_revenue": 46703.1,
   "net_revenue": 32691.24,
   "average_order_value": 993.6829787234043,
   "fulfillment_rate": 0.6595744680851063,
   "cancellation_rate": 0.19148936170212766,
   "gross_revenue_7d_ma": 52849.34,
   "total_orders_7d_ma": 53.142857142857146
  },
  {
   "date_day": "2026-08-10",
   "total_orders": 65,
   "gross_revenue": 56412.91,
   "net_revenue": 26113.8,
   "average_order_value": 867.8909230769231,
   "fulfillment_rate": 0.49230769230769234,
   "cancellation_rate": 0.3230769230769231,
   "gross_revenue_7d_ma": 53501.71571428571,
   "total_orders_7d_ma": 55.42857142857143
  },
  {
   "date_day": "2026-08-11",
   "total_orders": 60,
   "gross_revenue": 61431.57,
   "net_revenue": 39593.04,
   "average_order_value": 1023.8595,
   "fulfillment_rate": 0.6,
   "cancellation_rate": 0.21666666666666667,
   "gross_revenue_7d_ma": 54862.362857142856,
   "total_orders_7d_ma": 56.857142857142854
  },
  {
   "date_day": "2026-08-12",
   "total_orders": 57,
   "gross_revenue": 59902.77,
   "net_revenue": 26824.57,
   "average_order_value": 1050.9257894736843,
   "fulfillment_rate": 0.47368421052631576,
   "cancellation_rate": 0.22807017543859648,
   "gross_revenue_7d_ma": 54329.36857142857,
   "total_orders_7d_ma": 55.42857142857143
  },
  {
   "date_day": "2026-08-13",
   "total_orders": 54,
   "gross_revenue": 56493.65,
   "net_revenue": 32293.66,
   "average_order_value": 1046.1787037037036,
   "fulfillment_rate": 0.5555555555555556,
   "cancellation_rate": 0.2037037037037037,
   "gross_revenue_7d_ma": 55368.02285714286,
   "total_orders_7d_ma": 55.714285714285715
  },
  {
   "date_day": "2026-08-14",
   "total_orders": 55,
   "gross_revenue": 59577.19,
   "net_revenue": 33469.27,
   "average_order_value": 1083.2216363636364,
   "fulfillment_rate": 0.5454545454545454,
   "cancellation_rate": 0.14545454545454545,
   "gross_revenue_7d_ma": 56553.54714285714,
   "total_orders_7d_ma": 56.57142857142857
  },
  {
   "date_day": "2026-08-15",
   "total_orders": 57,
   "gross_revenue": 56507.42,
   "net_revenue": 39336.91,
   "average_order_value": 991.3582456140351,
   "fulfillment_rate": 0.6842105263157895,
   "cancellation_rate": 0.19298245614035087,
   "gross_revenue_7d_ma": 56718.37285714286,
   "total_orders_7d_ma": 56.42857142857143
  },
  {
   "date_day": "2026-08-16",
   "total_orders": 42,
   "gross_revenue": 44273.58,
   "net_revenue": 23882.38,
   "average_order_value": 1054.1328571428571,
   "fulfillment_rate": 0.5,
   "cancellation_rate": 0.23809523809523808,
   "gross_revenue_7d_ma": 56371.29857142857,
   "total_orders_7d_ma": 55.714285714285715
  },
  {
   "date_day": "2026-08-17",
   "total_orders": 58,
   "gross_revenue": 49121.44,
   "net_revenue": 27136.61,
   "average_order_value": 846.9213793103448,
   "fulfillment_rate": 0.5689655172413793,
   "cancellation_rate": 0.22413793103448276,
   "gross_revenue_7d_ma": 55329.66,
   "total_orders_7d_ma": 54.714285714285715
  },
  {
   "date_day": "2026-08-18",
   "total_orders": 57,
   "gross_revenue": 57054.66,
   "net_revenue": 29646.54,
   "average_order_value": 1000.958947368421,
   "fulfillment_rate": 0.5087719298245614,
   "cancellation_rate": 0.19298245614035087,
   "gross_revenue_7d_ma": 54704.387142857144,
   "total_orders_7d_ma": 54.285714285714285
  },
  {
   "date_day": "2026-08-19",
   "total_orders": 63,
   "gross_revenue": 65089.01,
   "net_revenue": 39628.72,
   "average_order_value": 1033.158888888889,
   "fulfillment_rate": 0.6190476190476191,
   "cancellation_rate": 0.2222222222222222,
   "gross_revenue_7d_ma": 55445.27857142857,
   "total_orders_7d_ma": 55.142857142857146
  },
  {
   "date_day": "2026-08-20",
   "total_orders": 51,
   "gross_revenue": 57821.52,
   "net_revenue": 37539.78,
   "average_order_value": 1133.755294117647,
   "fulfillment_rate": 0.6078431372549019,
   "cancellation_rate": 0.17647058823529413,
   "gross_revenue_7d_ma": 55634.974285714285,
   "total_orders_7d_ma": 54.714285714285715
  },
  {
   "date_day": "2026-08-21",
   "total_orders": 47,
   "gross_revenue": 48353.98,
   "net_revenue": 28510.94,
   "average_order_value": 1028.808085106383,
   "fulfillment_rate": 0.5319148936170213,
   "cancellation_rate": 0.2553191489361702,
   "gross_revenue_7d_ma": 54031.65857142857,
   "total_orders_7d_ma": 53.57142857142857
  },
  {
   "date_day": "2026-08-22",
   "total_orders": 61,
   "gross_revenue": 59167.3,
   "net_revenue": 39176.78,
   "average_order_value": 969.9557377049181,
   "fulfillment_rate": 0.5901639344262295,
   "cancellation_rate": 0.19672131147540983,
   "gross_revenue_7d_ma": 54411.64142857143,
   "total_orders_7d_ma": 54.142857142857146
  },
  {
   "date_day": "2026-08-23",
   "total_orders": 49,
   "gross_revenue": 46894.74,
   "net_revenue": 27055.49,
   "average_order_value": 957.0355102040817,
   "fulfillment_rate": 0.5306122448979592,
   "cancellation_rate": 0.22448979591836735,
   "gross_revenue_7d_ma": 54786.09285714286,
   "total_orders_7d_ma": 55.142857142857146
  },
  {
   "date_day": "2026-08-24",
   "total_orders": 52,
   "gross_revenue": 53602.24,
   "net_revenue": 32967.16,
   "average_order_value": 1030.8123076923077,
   "fulfillment_rate": 0.6153846153846154,
   "cancellation_rate": 0.25,
   "gross_revenue_7d_ma": 55426.20714285714,
   "total_orders_7d_ma": 54.285714285714285
  },
  {
   "date_day": "2026-08-25",
   "total_orders": 44,
   "gross_revenue": 47892.6,
   "net_revenue": 36430.4,
   "average_order_value": 1088.4681818181818,
   "fulfillment_rate": 0.7272727272727273,
   "cancellation_rate": 0.13636363636363635,
   "gross_revenue_7d_ma": 54117.34142857143,
   "total_orders_7d_ma": 52.42857142857143
  },
  {
   "date_day": "2026-08-26",
   "total_orders": 51,
   "gross_revenue": 50907.18,
   "net_revenue": 36166.97,
   "average_order_value": 998.18,
   "fulfillment_rate": 0.6862745098039216,
   "cancellation_rate": 0.19607843137254902,
   "gross_revenue_7d_ma": 52091.36571428571,
   "total_orders_7d_ma": 50.714285714285715
  },
  {
   "date_day": "2026-08-27",
   "total_orders": 46,
   "gross_revenue": 52796.44,
   "net_revenue": 30339.02,
   "average_order_value": 1147.7486956521739,
   "fulfillment_rate": 0.5652173913043478,
   "cancellation_rate": 0.10869565217391304,
   "gross_revenue_7d_ma": 51373.497142857144,
   "total_orders_7d_ma": 50.0
  },
  {
   "date_day": "2026-08-28",
   "total_orders": 58,
   "gross_revenue": 56478.18,
   "net_revenue": 34243.91,
   "average_order_value": 973.7617241379311,
   "fulfillment_rate": 0.5862068965517241,
   "cancellation_rate": 0.2413793103448276,
   "gross_revenue_7d_ma": 52534.09714285714,
   "total_orders_7d_ma": 51.57142857142857
  },
  {
   "date_day": "2026-08-29",
   "total_orders": 62,
   "gross_revenue": 62162.78,
   "net_revenue": 32503.99,
   "average_order_value": 1002.6254838709677,
   "fulfillment_rate": 0.4838709677419355,
   "cancellation_rate": 0.27419354838709675,
   "gross_revenue_7d_ma": 52962.02285714286,
   "total_orders_7d_ma": 51.714285714285715
  },
  {
   "date_day": "2026-08-30",
   "total_orders": 44,
   "gross_revenue": 40434.94,
   "net_revenue": 21682.67,
   "average_order_value": 918.9759090909091,
   "fulfillment_rate": 0.6136363636363636,
   "cancellation_rate": 0.20454545454545456,
   "gross_revenue_7d_ma": 52039.194285714286,
   "total_orders_7d_ma": 51.0
  },
  {
   "date_day": "2026-08-31",
   "total_orders": 61,
   "gross_revenue": 67491.45,
   "net_revenue": 44414.07,
   "average_order_value": 1106.417213114754,
   "fulfillment_rate": 0.6557377049180327,
   "cancellation_rate": 0.2459016393442623,
   "gross_revenue_7d_ma": 54023.36714285714,
   "total_orders_7d_ma": 52.285714285714285
  },
  {
   "date_day": "2026-09-01",
   "total_orders": 64,
   "gross_revenue": 65436.68,
   "net_revenue": 35262.74,
   "average_order_value": 1022.448125,
   "fulfillment_rate": 0.546875,
   "cancellation_rate": 0.15625,
   "gross_revenue_7d_ma": 56529.66428571429,
   "total_orders_7d_ma": 55.142857142857146
  },
  {
   "date_day": "2026-09-02",
   "total_orders": 56,
   "gross_revenue": 59216.12,
   "net_revenue": 31228.07,
   "average_order_value": 1057.4307142857142,
   "fulfillment_rate": 0.5,
   "cancellation_rate": 0.21428571428571427,
   "gross_revenue_7d_ma": 57716.65571428571,
   "total_orders_7d_ma": 55.857142857142854
  },
  {
   "date_day": "2026-09-03",
   "total_orders": 51,
   "gross_revenue": 54391.68,
   "net_revenue": 33433.33,
   "average_order_value": 1066.5035294117647,
   "fulfillment_rate": 0.5490196078431373,
   "cancellation_rate": 0.1568627450980392,
   "gross_revenue_7d_ma": 57944.54714285714,
   "total_orders_7d_ma": 56.57142857142857
  },
  {
   "date_day": "2026-09-04",
   "total_orders": 58,
   "gross_revenue": 66526.51,
   "net_revenue": 48156.34,
   "average_order_value": 1147.0087931034482,
   "fulfillment_rate": 0.6724137931034483,
   "cancellation_rate": 0.10344827586206896,
   "gross_revenue_7d_ma": 59380.02285714286,
   "total_orders_7d_ma": 56.57142857142857
  },
  {
   "date_day": "2026-09-05",
   "total_orders": 62,
   "gross_revenue": 64809.81,
   "net_revenue": 28351.03,
   "average_order_value": 1045.3195161290323,
   "fulfillment_rate": 0.46774193548387094,
   "cancellation_rate": 0.2903225806451613,
   "gross_revenue_7d_ma": 59758.17,
   "total_orders_7d_ma": 56.57142857142857
  },
  {
   "date_day": "2026-09-06",
   "total_orders": 53,
   "gross_revenue": 50064.08,
   "net_revenue": 23026.15,
   "average_order_value": 944.6052830188679,
   "fulfillment_rate": 0.5094339622641509,
   "cancellation_rate": 0.22641509433962265,
   "gross_revenue_7d_ma": 61133.76142857143,
   "total_orders_7d_ma": 57.857142857142854
  },
  {
   "date_day": "2026-09-07",
   "total_orders": 54,
   "gross_revenue": 57236.01,
   "net_revenue": 33496.43,
   "average_order_value": 1059.9261111111111,
   "fulfillment_rate": 0.5555555555555556,
   "cancellation_rate": 0.3333333333333333,
   "gross_revenue_7d_ma": 59668.69857142857,
   "total_orders_7d_ma": 56.857142857142854
  },
  {
   "date_day": "2026-09-08",
   "total_orders": 52,
   "gross_revenue": 47326.37,
   "net_revenue": 37434.39,
   "average_order_value": 910.1225,
   "fulfillment_rate": 0.7307692307692307,
   "cancellation_rate": 0.15384615384615385,
   "gross_revenue_7d_ma": 57081.51142857143,
   "total_orders_7d_ma": 55.142857142857146
  },
  {
   "date_day": "2026-09-09",
   "total_orders": 57,
   "gross_revenue": 63970.19,
   "net_revenue": 25867.75,
   "average_order_value": 1122.2840350877193,
   "fulfillment_rate": 0.43859649122807015,
   "cancellation_rate": 0.21052631578947367,
   "gross_revenue_7d_ma": 57760.66428571429,
   "total_orders_7d_ma": 55.285714285714285
  },
  {
   "date_day": "2026-09-10",
   "total_orders": 48,
   "gross_revenue": 54238.38,
   "net_revenue": 34249.57,
   "average_order_value": 1129.96625,
   "fulfillment_rate": 0.6041666666666666,
   "cancellation_rate": 0.25,
   "gross_revenue_7d_ma": 57738.764285714286,
   "total_orders_7d_ma": 54.857142857142854
  },
  {
   "date_day": "2026-09-11",
   "total_orders": 48,
   "gross_revenue": 53702.8,
   "net_revenue": 30338.9,
   "average_order_value": 1118.8083333333334,
   "fulfillment_rate": 0.5416666666666666,
   "cancellation_rate": 0.25,
   "gross_revenue_7d_ma": 55906.805714285714,
   "total_orders_7d_ma": 53.42857142857143
  },
  {
   "date_day": "2026-09-12",
   "total_orders": 48,
   "gross_revenue": 47597.56,
   "net_revenue": 25895.4,
   "average_order_value": 991.6158333333333,
   "fulfillment_rate": 0.5208333333333334,
   "cancellation_rate": 0.20833333333333334,
   "gross_revenue_7d_ma": 53447.91285714286,
   "total_orders_7d_ma": 51.42857142857143
  },
  {
   "date_day": "2026-09-13",
   "total_orders": 45,
   "gross_revenue": 44879.25,
   "net_revenue": 20085.2,
   "average_order_value": 997.3166666666667,
   "fulfillment_rate": 0.5333333333333333,
   "cancellation_rate": 0.2222222222222222,
   "gross_revenue_7d_ma": 52707.22285714286,
   "total_orders_7d_ma": 50.285714285714285
  },
  {
   "date_day": "2026-09-14",
   "total_orders": 46,
   "gross_revenue": 54161.53,
   "net_revenue": 34759.39,
   "average_order_value": 1177.4245652173913,
   "fulfillment_rate": 0.6739130434782609,
   "cancellation_rate": 0.15217391304347827,
   "gross_revenue_7d_ma": 52268.01142857143,
   "total_orders_7d_ma": 49.142857142857146
  },
  {
   "date_day": "2026-09-15",
   "total_orders": 61,
   "gross_revenue": 56193.46,
   "net_revenue": 23307.94,
   "average_order_value": 921.204262295082,
   "fulfillment_rate": 0.4426229508196721,
   "cancellation_rate": 0.21311475409836064,
   "gross_revenue_7d_ma": 53534.73857142857,
   "total_orders_7d_ma": 50.42857142857143
  },
  {
   "date_day": "2026-09-16",
   "total_orders": 62,
   "gross_revenue": 65681.42,
   "net_revenue": 43117.29,
   "average_order_value": 1059.377741935484,
   "fulfillment_rate": 0.6290322580645161,
   "cancellation_rate": 0.20967741935483872,
   "gross_revenue_7d_ma": 53779.2,
   "total_orders_7d_ma": 51.142857142857146
  },
  {
   "date_day": "2026-09-17",
   "total_orders": 50,
   "gross_revenue": 53058.99,
   "net_revenue": 23639.62,
   "average_order_value": 1061.1798,
   "fulfillment_rate": 0.46,
   "cancellation_rate": 0.32,
   "gross_revenue_7d_ma": 53610.71571428571,
   "total_orders_7d_ma": 51.42857142857143
  },
  {
   "date_day": "2026-09-18",
   "total_orders": 67,
   "gross_revenue": 59747.79,
   "net_revenue": 30928.34,
   "average_order_value": 891.7580597014926,
   "fulfillment_rate": 0.5373134328358209,
   "cancellation_rate": 0.22388059701492538,
   "gross_revenue_7d_ma": 54474.28571428572,
   "total_orders_7d_ma": 54.142857142857146
  },
  {
   "date_day": "2026-09-19",
   "total_orders": 55,
   "gross_revenue": 49699.46,
   "net_revenue": 28260.25,
   "average_order_value": 903.6265454545454,
   "fulfillment_rate": 0.5636363636363636,
   "cancellation_rate": 0.21818181818181817,
   "gross_revenue_7d_ma": 54774.55714285714,
   "total_orders_7d_ma": 55.142857142857146
  },
  {
   "date_day": "2026-09-20",
   "total_orders": 56,
   "gross_revenue": 60092.51,
   "net_revenue": 38868.21,
   "average_order_value": 1073.0805357142858,
   "fulfillment_rate": 0.6428571428571429,
   "cancellation_rate": 0.19642857142857142,
   "gross_revenue_7d_ma": 56947.88,
   "total_orders_7d_ma": 56.714285714285715
  },
  {
   "date_day": "2026-09-21",
   "total_orders": 59,
   "gross_revenue": 59136.73,
   "net_revenue": 28674.14,
   "average_order_value": 1002.3174576271186,
   "fulfillment_rate": 0.5423728813559322,
   "cancellation_rate": 0.2542372881355932,
   "gross_revenue_7d_ma": 57658.62285714286,
   "total_orders_7d_ma": 58.57142857142857
  },
  {
   "date_day": "2026-09-22",
   "total_orders": 54,
   "gross_revenue": 54739.67,
   "net_revenue": 36828.58,
   "average_order_value": 1013.6975925925926,
   "fulfillment_rate": 0.7037037037037037,
   "cancellation_rate": 0.12962962962962962,
   "gross_revenue_7d_ma": 57450.938571428575,
   "total_orders_7d_ma": 57.57142857142857
  },
  {
   "date_day": "2026-09-23",
   "total_orders": 51,
   "gross_revenue": 46853.99,
   "net_revenue": 26185.36,
   "average_order_value": 918.7056862745098,
   "fulfillment_rate": 0.5882352941176471,
   "cancellation_rate": 0.21568627450980393,
   "gross_revenue_7d_ma": 54761.305714285714,
   "total_orders_7d_ma": 56.0
  },
  {
   "date_day": "2026-09-24",
   "total_orders": 51,
   "gross_revenue": 49761.1,
   "net_revenue": 27241.43,
   "average_order_value": 975.7078431372549,
   "fulfillment_rate": 0.5294117647058824,
   "cancellation_rate": 0.27450980392156865,
   "gross_revenue_7d_ma": 54290.17857142857,
   "total_orders_7d_ma": 56.142857142857146
  },
  {
   "date_day": "2026-09-25",
   "total_orders": 50,
   "gross_revenue": 58551.58,
   "net_revenue": 37970.22,
   "average_order_value": 1171.0316,
   "fulfillment_rate": 0.64,
   "cancellation_rate": 0.18,
   "gross_revenue_7d_ma": 54119.29142857143,
   "total_orders_7d_ma": 53.714285714285715
  },
  {
   "date_day": "2026-09-26",
   "total_orders": 63,
   "gross_revenue": 63756.15,
   "net_revenue": 35400.37,
   "average_order_value": 1012.0023809523809,
   "fulfillment_rate": 0.5873015873015873,
   "cancellation_rate": 0.19047619047619047,
   "gross_revenue_7d_ma": 56127.39,
   "total_orders_7d_ma": 54.857142857142854
  },
  {
   "date_day": "2026-09-27",
   "total_orders": 51,
   "gross_revenue": 53742.23,
   "net_revenue": 29310.07,
   "average_order_value": 1053.7692156862745,
   "fulfillment_rate": 0.5294117647058824,
   "cancellation_rate": 0.23529411764705882,
   "gross_revenue_7d_ma": 55220.20714285714,
   "total_orders_7d_ma": 54.142857142857146
  },
  {
   "date_day": "2026-09-28",
   "total_orders": 45,
   "gross_revenue": 44624.54,
   "net_revenue": 20297.93,
   "average_order_value": 991.6564444444444,
   "fulfillment_rate": 0.4666666666666667,
   "cancellation_rate": 0.37777777777777777,
   "gross_revenue_7d_ma": 53147.037142857145,
   "total_orders_7d_ma": 52.142857142857146
  },
  {
   "date_day": "2026-09-29",
   "total_orders": 55,
   "gross_revenue": 49764.77,
   "net_revenue": 27767.27,
   "average_order_value": 904.814,
   "fulfillment_rate": 0.5454545454545454,
   "cancellation_rate": 0.16363636363636364,
   "gross_revenue_7d_ma": 52436.33714285714,
   "total_orders_7d_ma": 52.285714285714285
  },
  {
   "date_day": "2026-09-30",
   "total_orders": 55,
   "gross_revenue": 55913.19,
   "net_revenue": 24198.18,
   "average_order_value": 1016.6034545454545,
   "fulfillment_rate": 0.45454545454545453,
   "cancellation_rate": 0.32727272727272727,
   "gross_revenue_7d_ma": 53730.508571428574,
   "total_orders_7d_ma": 52.857142857142854
  },
  {
   "date_day": "2026-10-01",
   "total_orders": 57,
   "gross_revenue": 53605.82,
   "net_revenue": 29028.35,
   "average_order_value": 940.4529824561404,
   "fulfillment_rate": 0.5614035087719298,
   "cancellation_rate": 0.19298245614035087,
   "gross_revenue_7d_ma": 54279.75428571428,
   "total_orders_7d_ma": 53.714285714285715
  },
  {
   "date_day": "2026-10-02",
   "total_orders": 44,
   "gross_revenue": 41825.14,
   "net_revenue": 19753.04,
   "average_order_value": 950.5713636363637,
   "fulfillment_rate": 0.4772727272727273,
   "cancellation_rate": 0.20454545454545456,
   "gross_revenue_7d_ma": 51890.26285714286,
   "total_orders_7d_ma": 52.857142857142854
  },
  {
   "date_day": "2026-10-03",
   "total_orders": 49,
   "gross_revenue": 46082.53,
   "net_revenue": 25492.89,
   "average_order_value": 940.4597959183674,
   "fulfillment_rate": 0.4897959183673469,
   "cancellation_rate": 0.2857142857142857,
   "gross_revenue_7d_ma": 49365.46,
   "total_orders_7d_ma": 50.857142857142854
  },
  {
   "date_day": "2026-10-04",
   "total_orders": 49,
   "gross_revenue": 46822.56,
   "net_revenue": 25928.48,
   "average_order_value": 955.5624489795919,
   "fulfillment_rate": 0.5306122448979592,
   "cancellation_rate": 0.22448979591836735,
   "gross_revenue_7d_ma": 48376.93571428571,
   "total_orders_7d_ma": 50.57142857142857
  },
  {
   "date_day": "2026-10-05",
   "total_orders": 58,
   "gross_revenue": 49567.03,
   "net_revenue": 30835.8,
   "average_order_value": 854.6039655172414,
   "fulfillment_rate": 0.603448275862069,
   "cancellation_rate": 0.1724137931034483,
   "gross_revenue_7d_ma": 49083.00571428571,
   "total_orders_7d_ma": 52.42857142857143
  },
  {
   "date_day": "2026-10-06",
   "total_orders": 48,
   "gross_revenue": 48173.12,
   "net_revenue": 31749.48,
   "average_order_value": 1003.6066666666667,
   "fulfillment_rate": 0.625,
   "cancellation_rate": 0.14583333333333334,
   "gross_revenue_7d_ma": 48855.62714285714,
   "total_orders_7d_ma": 51.42857142857143
  },
  {
   "date_day": "2026-10-07",
   "total_orders": 67,
   "gross_revenue": 71781.04,
   "net_revenue": 43411.65,
   "average_order_value": 1071.3588059701492,
   "fulfillment_rate": 0.5671641791044776,
   "cancellation_rate": 0.208955223880597,
   "gross_revenue_7d_ma": 51122.462857142855,
   "total_orders_7d_ma": 53.142857142857146
  },
  {
   "date_day": "2026-10-08",
   "total_orders": 27,
   "gross_revenue": 26291.1,
   "net_revenue": 14296.81,
   "average_order_value": 973.7444444444444,
   "fulfillment_rate": 0.5185185185185185,
   "cancellation_rate": 0.18518518518518517,
   "gross_revenue_7d_ma": 47220.36,
   "total_orders_7d_ma": 48.857142857142854
  },
  {
   "date_day": "2026-10-09",
   "total_orders": 61,
   "gross_revenue": 57181.08,
   "net_revenue": 36460.36,
   "average_order_value": 937.3947540983606,
   "fulfillment_rate": 0.7049180327868853,
   "cancellation_rate": 0.09836065573770492,
   "gross_revenue_7d_ma": 49414.065714285716,
   "total_orders_7d_ma": 51.285714285714285
  },
  {
   "date_day": "2026-10-10",
   "total_orders": 62,
   "gross_revenue": 65578.11,
   "net_revenue": 25099.27,
   "average_order_value": 1057.7114516129031,
   "fulfillment_rate": 0.43548387096774194,
   "cancellation_rate": 0.2903225806451613,
   "gross_revenue_7d_ma": 52199.14857142857,
   "total_orders_7d_ma": 53.142857142857146
  },
  {
   "date_day": "2026-10-11",
   "total_orders": 56,
   "gross_revenue": 58642.85,
   "net_revenue": 33144.87,
   "average_order_value": 1047.19375,
   "fulfillment_rate": 0.5178571428571429,
   "cancellation_rate": 0.21428571428571427,
   "gross_revenue_7d_ma": 53887.76142857143,
   "total_orders_7d_ma": 54.142857142857146
  },
  {
   "date_day": "2026-10-12",
   "total_orders": 60,
   "gross_revenue": 58228.33,
   "net_revenue": 24786.89,
   "average_order_value": 970.4721666666667,
   "fulfillment_rate": 0.43333333333333335,
   "cancellation_rate": 0.31666666666666665,
   "gross_revenue_7d_ma": 55125.09,
   "total_orders_7d_ma": 54.42857142857143
  },
  {
   "date_day": "2026-10-13",
   "total_orders": 43,
   "gross_revenue": 48483.5,
   "net_revenue": 27127.37,
   "average_order_value": 1127.5232558139535,
   "fulfillment_rate": 0.5116279069767442,
   "cancellation_rate": 0.2558139534883721,
   "gross_revenue_7d_ma": 55169.43,
   "total_orders_7d_ma": 53.714285714285715
  },
  {
   "date_day": "2026-10-14",
   "total_orders": 51,
   "gross_revenue": 40967.74,
   "net_revenue": 24468.93,
   "average_order_value": 803.2890196078431,
   "fulfillment_rate": 0.6470588235294118,
   "cancellation_rate": 0.13725490196078433,
   "gross_revenue_7d_ma": 50767.53,
   "total_orders_7d_ma": 51.42857142857143
  },
  {
   "date_day": "2026-10-15",
   "total_orders": 58,
   "gross_revenue": 58587.33,
   "net_revenue": 32601.6,
   "average_order_value": 1010.1263793103449,
   "fulfillment_rate": 0.5517241379310345,
   "cancellation_rate": 0.3103448275862069,
   "gross_revenue_7d_ma": 55381.27714285714,
   "total_orders_7d_ma": 55.857142857142854
  },
  {
   "date_day": "2026-10-16",
   "total_orders": 49,
   "gross_revenue": 52997.62,
   "net_revenue": 40841.68,
   "average_order_value": 1081.5840816326531,
   "fulfillment_rate": 0.7755102040816326,
   "cancellation_rate": 0.10204081632653061,
   "gross_revenue_7d_ma": 54783.64,
   "total_orders_7d_ma": 54.142857142857146
  },
  {
   "date_day": "2026-10-17",
   "total_orders": 71,
   "gross_revenue": 78765.56,
   "net_revenue": 41180.19,
   "average_order_value": 1109.3740845070422,
   "fulfillment_rate": 0.5211267605633803,
   "cancellation_rate": 0.23943661971830985,
   "gross_revenue_7d_ma": 56667.561428571425,
   "total_orders_7d_ma": 55.42857142857143
  },
  {
   "date_day": "2026-10-18",
   "total_orders": 66,
   "gross_revenue": 71388.76,
   "net_revenue": 49754.33,
   "average_order_value": 1081.6478787878789,
   "fulfillment_rate": 0.7121212121212122,
   "cancellation_rate": 0.15151515151515152,
   "gross_revenue_7d_ma": 58488.40571428571,
   "total_orders_7d_ma": 56.857142857142854
  },
  {
   "date_day": "2026-10-19",
   "total_orders": 52,
   "gross_revenue": 46187.82,
   "net_revenue": 25788.14,
   "average_order_value": 888.2273076923077,
   "fulfillment_rate": 0.5576923076923077,
   "cancellation_rate": 0.25,
   "gross_revenue_7d_ma": 56768.33285714286,
   "total_orders_7d_ma": 55.714285714285715
  },
  {
   "date_day": "2026-10-20",
   "total_orders": 52,
   "gross_revenue": 53534.44,
   "net_revenue": 32465.43,
   "average_order_value": 1029.5084615384615,
   "fulfillment_rate": 0.5192307692307693,
   "cancellation_rate": 0.15384615384615385,
   "gross_revenue_7d_ma": 57489.89571428571,
   "total_orders_7d_ma": 57.0
  },
  {
   "date_day": "2026-10-21",
   "total_orders": 53,
   "gross_revenue": 54131.63,
   "net_revenue": 34731.54,
   "average_order_value": 1021.3515094339623,
   "fulfillment_rate": 0.6037735849056604,
   "cancellation_rate": 0.1509433962264151,
   "gross_revenue_7d_ma": 59370.45142857143,
   "total_orders_7d_ma": 57.285714285714285
  },
  {
   "date_day": "2026-10-22",
   "total_orders": 45,
   "gross_revenue": 51151.63,
   "net_revenue": 30834.53,
   "average_order_value": 1136.702888888889,
   "fulfillment_rate": 0.6,
   "cancellation_rate": 0.2,
   "gross_revenue_7d_ma": 58308.20857142857,
   "total_orders_7d_ma": 55.42857142857143
  },
  {
   "date_day": "2026-10-23",
   "total_orders": 58,
   "gross_revenue": 54442.91,
   "net_revenue": 34406.55,
   "average_order_value": 938.6708620689656,
   "fulfillment_rate": 0.6206896551724138,
   "cancellation_rate": 0.13793103448275862,
   "gross_revenue_7d_ma": 58514.67857142857,
   "total_orders_7d_ma": 56.714285714285715
  },
  {
   "date_day": "2026-10-24",
   "total_orders": 25,
   "gross_revenue": 24142.44,
   "net_revenue": 18659.59,
   "average_order_value": 965.6976,
   "fulfillment_rate": 0.68,
   "cancellation_rate": 0.08,
   "gross_revenue_7d_ma": 50711.375714285714,
   "total_orders_7d_ma": 50.142857142857146
  }
 ],
 "windows": {
  "7": {
   "metrics": {
    "current": {
     "orders": 351,
     "revenue": 354979.63,
     "aov": 1011.3379772079772,
     "fulfillment_rate": 0.6125356125356125,
     "customers": 254
    },
    "previous": {
     "orders": 388,
     "revenue": 396672.93,
     "aov": 1022.352912371134,
     "fulfillment_rate": 0.5592783505154639,
     "customers": 270
    }
   },
   "status": [
    {
     "label": "delivered",
     "orders": 161,
     "revenue": 170839.86
    },
    {
     "label": "shipped",
     "orders": 54,
     "revenue": 55800.25
    },
    {
     "label": "processing",
     "orders": 40,
     "revenue": 37266.65
    },
    {
     "label": "pending",
     "orders": 38,
     "revenue": 35969.43
    },
    {
     "label": "refunded",
     "orders": 30,
     "revenue": 29522.03
    },
    {
     "label": "cancelled",
     "orders": 28,
     "revenue": 25581.41
    }
   ],
   "segments": [
    {
     "label": "loyal_customer",
     "orders": 329,
     "revenue": 333160.71,
     "customers": 234
    },
    {
     "label": "potential_loyalist",
     "orders": 12,
     "revenue": 13205.19,
     "customers": 12
    },
    {
     "label": "vip",
     "orders": 10,
     "revenue": 8613.73,
     "customers": 8
    }
   ],
   "countries": [
    {
     "label": "US",
     "orders": 114,
     "revenue": 115943.82,
     "aov": 1017.051052631579
    },
    {
     "label": "FR",
     "orders": 49,
     "revenue": 56396.48,
     "aov": 1150.9485714285715
    },
    {
     "label": "AU",
     "orders": 53,
     "revenue": 51899.48,
     "aov": 979.2354716981132
    },
    {
     "label": "DE",
     "orders": 51,
     "revenue": 47463.34,
     "aov": 930.653725490196
    },
    {
     "label": "CA",
     "orders": 49,
     "revenue": 47018.9,
     "aov": 959.5693877551021
    },
    {
     "label": "GB",
     "orders": 35,
     "revenue": 36257.61,
     "aov": 1035.9317142857142
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
     "revenue": 148591.08
    },
    {
     "label": "apple_pay",
     "orders": 74,
     "revenue": 76066.29
    },
    {
     "label": "paypal",
     "orders": 66,
     "revenue": 73590.63
    },
    {
     "label": "bank_transfer",
     "orders": 61,
     "revenue": 56731.63
    }
   ]
  },
  "30": {
   "metrics": {
    "current": {
     "orders": 1580,
     "revenue": 1584912.55,
     "aov": 1003.1092088607595,
     "fulfillment_rate": 0.5658227848101266,
     "customers": 470
    },
    "previous": {
     "orders": 1630,
     "revenue": 1668793.06,
     "aov": 1023.7994233128834,
     "fulfillment_rate": 0.5674846625766872,
     "customers": 487
    }
   },
   "status": [
    {
     "label": "delivered",
     "orders": 710,
     "revenue": 721748.18
    },
    {
     "label": "shipped",
     "orders": 184,
     "revenue": 186043.63
    },
    {
     "label": "pending",
     "orders": 180,
     "revenue": 178695.5
    },
    {
     "label": "processing",
     "orders": 177,
     "revenue": 191252.2
    },
    {
     "label": "cancelled",
     "orders": 175,
     "revenue": 167561.82
    },
    {
     "label": "refunded",
     "orders": 154,
     "revenue": 139611.22
    }
   ],
   "segments": [
    {
     "label": "loyal_customer",
     "orders": 1479,
     "revenue": 1487178.0,
     "customers": 429
    },
    {
     "label": "vip",
     "orders": 54,
     "revenue": 52158.78,
     "customers": 13
    },
    {
     "label": "potential_loyalist",
     "orders": 47,
     "revenue": 45575.77,
     "customers": 28
    }
   ],
   "countries": [
    {
     "label": "US",
     "orders": 505,
     "revenue": 500009.19,
     "aov": 990.1172079207921
    },
    {
     "label": "AU",
     "orders": 250,
     "revenue": 249661.15,
     "aov": 998.6446
    },
    {
     "label": "DE",
     "orders": 221,
     "revenue": 217031.54,
     "aov": 982.0431674208145
    },
    {
     "label": "CA",
     "orders": 214,
     "revenue": 214031.44,
     "aov": 1000.1469158878505
    },
    {
     "label": "FR",
     "orders": 204,
     "revenue": 207878.75,
     "aov": 1019.0134803921569
    },
    {
     "label": "GB",
     "orders": 186,
     "revenue": 196300.48,
     "aov": 1055.378924731183
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
     "revenue": 636599.43
    },
    {
     "label": "apple_pay",
     "orders": 310,
     "revenue": 315429.04
    },
    {
     "label": "paypal",
     "orders": 309,
     "revenue": 328627.03
    },
    {
     "label": "bank_transfer",
     "orders": 301,
     "revenue": 304257.05
    }
   ]
  },
  "90": {
   "metrics": {
    "current": {
     "orders": 4867,
     "revenue": 4929545.91,
     "aov": 1012.8510191082803,
     "fulfillment_rate": 0.5720156153688104,
     "customers": 500
    },
    "previous": {
     "orders": 29,
     "revenue": 30578.56,
     "aov": 1054.433103448276,
     "fulfillment_rate": 0.4482758620689655,
     "customers": 29
    }
   },
   "status": [
    {
     "label": "delivered",
     "orders": 2220,
     "revenue": 2291649.16
    },
    {
     "label": "shipped",
     "orders": 564,
     "revenue": 566186.24
    },
    {
     "label": "cancelled",
     "orders": 545,
     "revenue": 552341.58
    },
    {
     "label": "processing",
     "orders": 539,
     "revenue": 551821.87
    },
    {
     "label": "pending",
     "orders": 520,
     "revenue": 509807.67
    },
    {
     "label": "refunded",
     "orders": 479,
     "revenue": 457739.39
    }
   ],
   "segments": [
    {
     "label": "loyal_customer",
     "orders": 4409,
     "revenue": 4465200.54,
     "customers": 435
    },
    {
     "label": "at_risk",
     "orders": 160,
     "revenue": 172583.42,
     "customers": 23
    },
    {
     "label": "vip",
     "orders": 170,
     "revenue": 170153.16,
     "customers": 13
    },
    {
     "label": "potential_loyalist",
     "orders": 128,
     "revenue": 121608.79,
     "customers": 29
    }
   ],
   "countries": [
    {
     "label": "US",
     "orders": 1521,
     "revenue": 1529371.9,
     "aov": 1005.5042077580539
    },
    {
     "label": "DE",
     "orders": 743,
     "revenue": 749950.97,
     "aov": 1009.3552759084791
    },
    {
     "label": "AU",
     "orders": 744,
     "revenue": 746962.18,
     "aov": 1003.9814247311828
    },
    {
     "label": "FR",
     "orders": 656,
     "revenue": 674178.38,
     "aov": 1027.7109451219512
    },
    {
     "label": "CA",
     "orders": 613,
     "revenue": 633799.68,
     "aov": 1033.9309624796085
    },
    {
     "label": "GB",
     "orders": 590,
     "revenue": 595282.8,
     "aov": 1008.9538983050847
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
     "revenue": 1975266.96
    },
    {
     "label": "paypal",
     "orders": 978,
     "revenue": 1028884.09
    },
    {
     "label": "bank_transfer",
     "orders": 955,
     "revenue": 962169.27
    },
    {
     "label": "apple_pay",
     "orders": 946,
     "revenue": 963225.59
    }
   ]
  }
 }
};
