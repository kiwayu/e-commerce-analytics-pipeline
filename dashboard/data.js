window.DASHBOARD_DATA = {
 "as_of": "2026-10-24",
 "generated_at": "2026-10-24T10:41:47+00:00",
 "pipeline": {
  "last_run": "2026-10-24T11:41:46.412523+01:00",
  "raw_loaded_at": "2026-10-24T11:28:16.859562+01:00",
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
   "elapsed_seconds": 13.4
  }
 },
 "daily": [
  {
   "date_day": "2026-07-27",
   "total_orders": 67,
   "gross_revenue": 66135.82,
   "net_revenue": 43221.37,
   "average_order_value": 987.1017910447761,
   "fulfillment_rate": 0.5970149253731343,
   "cancellation_rate": 0.23880597014925373,
   "gross_revenue_7d_ma": 45269.33,
   "total_orders_7d_ma": 46.0
  },
  {
   "date_day": "2026-07-28",
   "total_orders": 57,
   "gross_revenue": 53869.12,
   "net_revenue": 29478.81,
   "average_order_value": 945.0722807017544,
   "fulfillment_rate": 0.5789473684210527,
   "cancellation_rate": 0.19298245614035087,
   "gross_revenue_7d_ma": 48135.93,
   "total_orders_7d_ma": 49.67
  },
  {
   "date_day": "2026-07-29",
   "total_orders": 67,
   "gross_revenue": 72372.35,
   "net_revenue": 45031.8,
   "average_order_value": 1080.1843283582089,
   "fulfillment_rate": 0.6119402985074627,
   "cancellation_rate": 0.13432835820895522,
   "gross_revenue_7d_ma": 54195.03,
   "total_orders_7d_ma": 54.0
  },
  {
   "date_day": "2026-07-30",
   "total_orders": 60,
   "gross_revenue": 58402.85,
   "net_revenue": 36717.18,
   "average_order_value": 973.3808333333334,
   "fulfillment_rate": 0.6333333333333333,
   "cancellation_rate": 0.2833333333333333,
   "gross_revenue_7d_ma": 55036.6,
   "total_orders_7d_ma": 55.2
  },
  {
   "date_day": "2026-07-31",
   "total_orders": 42,
   "gross_revenue": 41976.56,
   "net_revenue": 24221.11,
   "average_order_value": 999.4419047619048,
   "fulfillment_rate": 0.5952380952380952,
   "cancellation_rate": 0.16666666666666666,
   "gross_revenue_7d_ma": 52859.92,
   "total_orders_7d_ma": 53.0
  },
  {
   "date_day": "2026-08-01",
   "total_orders": 63,
   "gross_revenue": 64466.92,
   "net_revenue": 42868.6,
   "average_order_value": 1023.2844444444445,
   "fulfillment_rate": 0.6349206349206349,
   "cancellation_rate": 0.1111111111111111,
   "gross_revenue_7d_ma": 54518.07,
   "total_orders_7d_ma": 54.43
  },
  {
   "date_day": "2026-08-02",
   "total_orders": 60,
   "gross_revenue": 51563.32,
   "net_revenue": 25636.57,
   "average_order_value": 859.3886666666667,
   "fulfillment_rate": 0.5666666666666667,
   "cancellation_rate": 0.2833333333333333,
   "gross_revenue_7d_ma": 58398.13,
   "total_orders_7d_ma": 59.43
  },
  {
   "date_day": "2026-08-03",
   "total_orders": 50,
   "gross_revenue": 48246.78,
   "net_revenue": 33557.9,
   "average_order_value": 964.9356,
   "fulfillment_rate": 0.66,
   "cancellation_rate": 0.18,
   "gross_revenue_7d_ma": 55842.56,
   "total_orders_7d_ma": 57.0
  },
  {
   "date_day": "2026-08-04",
   "total_orders": 48,
   "gross_revenue": 46920.3,
   "net_revenue": 28701.93,
   "average_order_value": 977.50625,
   "fulfillment_rate": 0.6041666666666666,
   "cancellation_rate": 0.14583333333333334,
   "gross_revenue_7d_ma": 54849.87,
   "total_orders_7d_ma": 55.71
  },
  {
   "date_day": "2026-08-05",
   "total_orders": 66,
   "gross_revenue": 61540.3,
   "net_revenue": 34285.42,
   "average_order_value": 932.4287878787878,
   "fulfillment_rate": 0.6060606060606061,
   "cancellation_rate": 0.18181818181818182,
   "gross_revenue_7d_ma": 53302.43,
   "total_orders_7d_ma": 55.57
  },
  {
   "date_day": "2026-08-06",
   "total_orders": 54,
   "gross_revenue": 49380.88,
   "net_revenue": 26035.91,
   "average_order_value": 914.4607407407408,
   "fulfillment_rate": 0.48148148148148145,
   "cancellation_rate": 0.2037037037037037,
   "gross_revenue_7d_ma": 52013.58,
   "total_orders_7d_ma": 54.71
  },
  {
   "date_day": "2026-08-07",
   "total_orders": 50,
   "gross_revenue": 48663.06,
   "net_revenue": 30165.44,
   "average_order_value": 973.2612,
   "fulfillment_rate": 0.56,
   "cancellation_rate": 0.28,
   "gross_revenue_7d_ma": 52968.79,
   "total_orders_7d_ma": 55.86
  },
  {
   "date_day": "2026-08-08",
   "total_orders": 56,
   "gross_revenue": 52142.57,
   "net_revenue": 29054.68,
   "average_order_value": 931.1173214285715,
   "fulfillment_rate": 0.5357142857142857,
   "cancellation_rate": 0.19642857142857142,
   "gross_revenue_7d_ma": 51208.17,
   "total_orders_7d_ma": 54.86
  },
  {
   "date_day": "2026-08-09",
   "total_orders": 49,
   "gross_revenue": 47268.05,
   "net_revenue": 33327.5,
   "average_order_value": 964.6540816326531,
   "fulfillment_rate": 0.6530612244897959,
   "cancellation_rate": 0.1836734693877551,
   "gross_revenue_7d_ma": 50594.56,
   "total_orders_7d_ma": 53.29
  },
  {
   "date_day": "2026-08-10",
   "total_orders": 64,
   "gross_revenue": 53085.8,
   "net_revenue": 25285.19,
   "average_order_value": 829.465625,
   "fulfillment_rate": 0.484375,
   "cancellation_rate": 0.328125,
   "gross_revenue_7d_ma": 51285.85,
   "total_orders_7d_ma": 55.29
  },
  {
   "date_day": "2026-08-11",
   "total_orders": 58,
   "gross_revenue": 57833.13,
   "net_revenue": 37142.96,
   "average_order_value": 997.1229310344828,
   "fulfillment_rate": 0.6206896551724138,
   "cancellation_rate": 0.20689655172413793,
   "gross_revenue_7d_ma": 52844.83,
   "total_orders_7d_ma": 56.71
  },
  {
   "date_day": "2026-08-12",
   "total_orders": 54,
   "gross_revenue": 50483.28,
   "net_revenue": 19947.61,
   "average_order_value": 934.8755555555556,
   "fulfillment_rate": 0.46296296296296297,
   "cancellation_rate": 0.24074074074074073,
   "gross_revenue_7d_ma": 51265.25,
   "total_orders_7d_ma": 55.0
  },
  {
   "date_day": "2026-08-13",
   "total_orders": 57,
   "gross_revenue": 55714.34,
   "net_revenue": 31833.9,
   "average_order_value": 977.4445614035088,
   "fulfillment_rate": 0.543859649122807,
   "cancellation_rate": 0.21052631578947367,
   "gross_revenue_7d_ma": 52170.03,
   "total_orders_7d_ma": 55.43
  },
  {
   "date_day": "2026-08-14",
   "total_orders": 58,
   "gross_revenue": 61242.33,
   "net_revenue": 34574.76,
   "average_order_value": 1055.9022413793105,
   "fulfillment_rate": 0.5517241379310345,
   "cancellation_rate": 0.13793103448275862,
   "gross_revenue_7d_ma": 53967.07,
   "total_orders_7d_ma": 56.57
  },
  {
   "date_day": "2026-08-15",
   "total_orders": 55,
   "gross_revenue": 53666.21,
   "net_revenue": 37325.0,
   "average_order_value": 975.7492727272727,
   "fulfillment_rate": 0.7090909090909091,
   "cancellation_rate": 0.16363636363636364,
   "gross_revenue_7d_ma": 54184.73,
   "total_orders_7d_ma": 56.43
  },
  {
   "date_day": "2026-08-16",
   "total_orders": 41,
   "gross_revenue": 39098.24,
   "net_revenue": 19411.35,
   "average_order_value": 953.6156097560976,
   "fulfillment_rate": 0.4634146341463415,
   "cancellation_rate": 0.2682926829268293,
   "gross_revenue_7d_ma": 53017.62,
   "total_orders_7d_ma": 55.29
  },
  {
   "date_day": "2026-08-17",
   "total_orders": 59,
   "gross_revenue": 47388.14,
   "net_revenue": 27822.67,
   "average_order_value": 803.188813559322,
   "fulfillment_rate": 0.5932203389830508,
   "cancellation_rate": 0.23728813559322035,
   "gross_revenue_7d_ma": 52203.67,
   "total_orders_7d_ma": 54.57
  },
  {
   "date_day": "2026-08-18",
   "total_orders": 56,
   "gross_revenue": 55953.1,
   "net_revenue": 27323.56,
   "average_order_value": 999.1625,
   "fulfillment_rate": 0.5,
   "cancellation_rate": 0.17857142857142858,
   "gross_revenue_7d_ma": 51935.09,
   "total_orders_7d_ma": 54.29
  },
  {
   "date_day": "2026-08-19",
   "total_orders": 66,
   "gross_revenue": 66159.75,
   "net_revenue": 40305.59,
   "average_order_value": 1002.4204545454545,
   "fulfillment_rate": 0.6060606060606061,
   "cancellation_rate": 0.22727272727272727,
   "gross_revenue_7d_ma": 54174.59,
   "total_orders_7d_ma": 56.0
  },
  {
   "date_day": "2026-08-20",
   "total_orders": 48,
   "gross_revenue": 49025.2,
   "net_revenue": 29825.83,
   "average_order_value": 1021.3583333333333,
   "fulfillment_rate": 0.6041666666666666,
   "cancellation_rate": 0.16666666666666666,
   "gross_revenue_7d_ma": 53219.0,
   "total_orders_7d_ma": 54.71
  },
  {
   "date_day": "2026-08-21",
   "total_orders": 48,
   "gross_revenue": 46134.39,
   "net_revenue": 29374.26,
   "average_order_value": 961.133125,
   "fulfillment_rate": 0.5416666666666666,
   "cancellation_rate": 0.2708333333333333,
   "gross_revenue_7d_ma": 51060.72,
   "total_orders_7d_ma": 53.29
  },
  {
   "date_day": "2026-08-22",
   "total_orders": 61,
   "gross_revenue": 57808.2,
   "net_revenue": 37066.66,
   "average_order_value": 947.6754098360656,
   "fulfillment_rate": 0.5737704918032787,
   "cancellation_rate": 0.19672131147540983,
   "gross_revenue_7d_ma": 51652.43,
   "total_orders_7d_ma": 54.14
  },
  {
   "date_day": "2026-08-23",
   "total_orders": 49,
   "gross_revenue": 44592.01,
   "net_revenue": 27822.35,
   "average_order_value": 910.0410204081633,
   "fulfillment_rate": 0.5510204081632653,
   "cancellation_rate": 0.22448979591836735,
   "gross_revenue_7d_ma": 52437.26,
   "total_orders_7d_ma": 55.29
  },
  {
   "date_day": "2026-08-24",
   "total_orders": 54,
   "gross_revenue": 53662.5,
   "net_revenue": 33145.47,
   "average_order_value": 993.75,
   "fulfillment_rate": 0.6111111111111112,
   "cancellation_rate": 0.24074074074074073,
   "gross_revenue_7d_ma": 53333.59,
   "total_orders_7d_ma": 54.57
  },
  {
   "date_day": "2026-08-25",
   "total_orders": 43,
   "gross_revenue": 47552.82,
   "net_revenue": 36436.92,
   "average_order_value": 1105.879534883721,
   "fulfillment_rate": 0.7209302325581395,
   "cancellation_rate": 0.13953488372093023,
   "gross_revenue_7d_ma": 52133.55,
   "total_orders_7d_ma": 52.71
  },
  {
   "date_day": "2026-08-26",
   "total_orders": 51,
   "gross_revenue": 48180.39,
   "net_revenue": 35462.77,
   "average_order_value": 944.7135294117647,
   "fulfillment_rate": 0.7058823529411765,
   "cancellation_rate": 0.19607843137254902,
   "gross_revenue_7d_ma": 49565.07,
   "total_orders_7d_ma": 50.57
  },
  {
   "date_day": "2026-08-27",
   "total_orders": 46,
   "gross_revenue": 48546.46,
   "net_revenue": 26540.23,
   "average_order_value": 1055.3578260869565,
   "fulfillment_rate": 0.5434782608695652,
   "cancellation_rate": 0.10869565217391304,
   "gross_revenue_7d_ma": 49496.68,
   "total_orders_7d_ma": 50.29
  },
  {
   "date_day": "2026-08-28",
   "total_orders": 56,
   "gross_revenue": 55643.24,
   "net_revenue": 33905.74,
   "average_order_value": 993.6292857142857,
   "fulfillment_rate": 0.5892857142857143,
   "cancellation_rate": 0.23214285714285715,
   "gross_revenue_7d_ma": 50855.09,
   "total_orders_7d_ma": 51.43
  },
  {
   "date_day": "2026-08-29",
   "total_orders": 64,
   "gross_revenue": 60242.69,
   "net_revenue": 32205.15,
   "average_order_value": 941.29203125,
   "fulfillment_rate": 0.5,
   "cancellation_rate": 0.265625,
   "gross_revenue_7d_ma": 51202.87,
   "total_orders_7d_ma": 51.86
  },
  {
   "date_day": "2026-08-30",
   "total_orders": 43,
   "gross_revenue": 39486.93,
   "net_revenue": 20127.66,
   "average_order_value": 918.3006976744186,
   "fulfillment_rate": 0.6046511627906976,
   "cancellation_rate": 0.20930232558139536,
   "gross_revenue_7d_ma": 50473.58,
   "total_orders_7d_ma": 51.0
  },
  {
   "date_day": "2026-08-31",
   "total_orders": 62,
   "gross_revenue": 64391.31,
   "net_revenue": 42200.7,
   "average_order_value": 1038.5695161290323,
   "fulfillment_rate": 0.6451612903225806,
   "cancellation_rate": 0.25806451612903225,
   "gross_revenue_7d_ma": 52006.26,
   "total_orders_7d_ma": 52.14
  },
  {
   "date_day": "2026-09-01",
   "total_orders": 62,
   "gross_revenue": 53881.48,
   "net_revenue": 28134.11,
   "average_order_value": 869.056129032258,
   "fulfillment_rate": 0.532258064516129,
   "cancellation_rate": 0.16129032258064516,
   "gross_revenue_7d_ma": 52910.36,
   "total_orders_7d_ma": 54.86
  },
  {
   "date_day": "2026-09-02",
   "total_orders": 58,
   "gross_revenue": 62218.94,
   "net_revenue": 35655.69,
   "average_order_value": 1072.7403448275861,
   "fulfillment_rate": 0.5344827586206896,
   "cancellation_rate": 0.1896551724137931,
   "gross_revenue_7d_ma": 54915.86,
   "total_orders_7d_ma": 55.86
  },
  {
   "date_day": "2026-09-03",
   "total_orders": 50,
   "gross_revenue": 51245.78,
   "net_revenue": 30906.58,
   "average_order_value": 1024.9156,
   "fulfillment_rate": 0.56,
   "cancellation_rate": 0.18,
   "gross_revenue_7d_ma": 55301.48,
   "total_orders_7d_ma": 56.43
  },
  {
   "date_day": "2026-09-04",
   "total_orders": 59,
   "gross_revenue": 63240.66,
   "net_revenue": 44925.85,
   "average_order_value": 1071.875593220339,
   "fulfillment_rate": 0.6440677966101694,
   "cancellation_rate": 0.1016949152542373,
   "gross_revenue_7d_ma": 56386.83,
   "total_orders_7d_ma": 56.86
  },
  {
   "date_day": "2026-09-05",
   "total_orders": 63,
   "gross_revenue": 61020.22,
   "net_revenue": 26616.36,
   "average_order_value": 968.5749206349207,
   "fulfillment_rate": 0.47619047619047616,
   "cancellation_rate": 0.2857142857142857,
   "gross_revenue_7d_ma": 56497.9,
   "total_orders_7d_ma": 56.71
  },
  {
   "date_day": "2026-09-06",
   "total_orders": 50,
   "gross_revenue": 43576.8,
   "net_revenue": 20091.85,
   "average_order_value": 871.536,
   "fulfillment_rate": 0.5,
   "cancellation_rate": 0.24,
   "gross_revenue_7d_ma": 57082.17,
   "total_orders_7d_ma": 57.71
  },
  {
   "date_day": "2026-09-07",
   "total_orders": 52,
   "gross_revenue": 54856.97,
   "net_revenue": 31214.48,
   "average_order_value": 1054.9417307692308,
   "fulfillment_rate": 0.5192307692307693,
   "cancellation_rate": 0.34615384615384615,
   "gross_revenue_7d_ma": 55720.12,
   "total_orders_7d_ma": 56.29
  },
  {
   "date_day": "2026-09-08",
   "total_orders": 56,
   "gross_revenue": 48688.4,
   "net_revenue": 40070.1,
   "average_order_value": 869.4357142857143,
   "fulfillment_rate": 0.75,
   "cancellation_rate": 0.14285714285714285,
   "gross_revenue_7d_ma": 54978.25,
   "total_orders_7d_ma": 55.43
  },
  {
   "date_day": "2026-09-09",
   "total_orders": 55,
   "gross_revenue": 58217.08,
   "net_revenue": 24437.56,
   "average_order_value": 1058.4923636363637,
   "fulfillment_rate": 0.45454545454545453,
   "cancellation_rate": 0.2,
   "gross_revenue_7d_ma": 54406.56,
   "total_orders_7d_ma": 55.0
  },
  {
   "date_day": "2026-09-10",
   "total_orders": 49,
   "gross_revenue": 51112.54,
   "net_revenue": 29514.81,
   "average_order_value": 1043.1130612244897,
   "fulfillment_rate": 0.5918367346938775,
   "cancellation_rate": 0.2653061224489796,
   "gross_revenue_7d_ma": 54387.52,
   "total_orders_7d_ma": 54.86
  },
  {
   "date_day": "2026-09-11",
   "total_orders": 50,
   "gross_revenue": 55618.16,
   "net_revenue": 33373.69,
   "average_order_value": 1112.3632,
   "fulfillment_rate": 0.54,
   "cancellation_rate": 0.24,
   "gross_revenue_7d_ma": 53298.6,
   "total_orders_7d_ma": 53.57
  },
  {
   "date_day": "2026-09-12",
   "total_orders": 46,
   "gross_revenue": 42862.53,
   "net_revenue": 22092.61,
   "average_order_value": 931.7941304347826,
   "fulfillment_rate": 0.5217391304347826,
   "cancellation_rate": 0.1956521739130435,
   "gross_revenue_7d_ma": 50704.64,
   "total_orders_7d_ma": 51.14
  },
  {
   "date_day": "2026-09-13",
   "total_orders": 46,
   "gross_revenue": 45623.97,
   "net_revenue": 18239.42,
   "average_order_value": 991.8254347826087,
   "fulfillment_rate": 0.5434782608695652,
   "cancellation_rate": 0.21739130434782608,
   "gross_revenue_7d_ma": 50997.09,
   "total_orders_7d_ma": 50.57
  },
  {
   "date_day": "2026-09-14",
   "total_orders": 43,
   "gross_revenue": 46595.72,
   "net_revenue": 28429.75,
   "average_order_value": 1083.6213953488373,
   "fulfillment_rate": 0.6744186046511628,
   "cancellation_rate": 0.18604651162790697,
   "gross_revenue_7d_ma": 49816.91,
   "total_orders_7d_ma": 49.29
  },
  {
   "date_day": "2026-09-15",
   "total_orders": 62,
   "gross_revenue": 57238.16,
   "net_revenue": 23775.53,
   "average_order_value": 923.1961290322581,
   "fulfillment_rate": 0.46774193548387094,
   "cancellation_rate": 0.1935483870967742,
   "gross_revenue_7d_ma": 51038.31,
   "total_orders_7d_ma": 50.14
  },
  {
   "date_day": "2026-09-16",
   "total_orders": 63,
   "gross_revenue": 63066.1,
   "net_revenue": 38721.67,
   "average_order_value": 1001.0492063492063,
   "fulfillment_rate": 0.6031746031746031,
   "cancellation_rate": 0.20634920634920634,
   "gross_revenue_7d_ma": 51731.03,
   "total_orders_7d_ma": 51.29
  },
  {
   "date_day": "2026-09-17",
   "total_orders": 51,
   "gross_revenue": 51100.72,
   "net_revenue": 23459.96,
   "average_order_value": 1001.9749019607843,
   "fulfillment_rate": 0.47058823529411764,
   "cancellation_rate": 0.3137254901960784,
   "gross_revenue_7d_ma": 51729.34,
   "total_orders_7d_ma": 51.57
  },
  {
   "date_day": "2026-09-18",
   "total_orders": 67,
   "gross_revenue": 54538.86,
   "net_revenue": 27802.76,
   "average_order_value": 814.0128358208955,
   "fulfillment_rate": 0.5223880597014925,
   "cancellation_rate": 0.23880597014925373,
   "gross_revenue_7d_ma": 51575.15,
   "total_orders_7d_ma": 54.0
  },
  {
   "date_day": "2026-09-19",
   "total_orders": 51,
   "gross_revenue": 42444.75,
   "net_revenue": 24322.08,
   "average_order_value": 832.25,
   "fulfillment_rate": 0.5882352941176471,
   "cancellation_rate": 0.21568627450980393,
   "gross_revenue_7d_ma": 51515.47,
   "total_orders_7d_ma": 54.71
  },
  {
   "date_day": "2026-09-20",
   "total_orders": 58,
   "gross_revenue": 64031.24,
   "net_revenue": 39290.44,
   "average_order_value": 1103.9868965517242,
   "fulfillment_rate": 0.6379310344827587,
   "cancellation_rate": 0.1896551724137931,
   "gross_revenue_7d_ma": 54145.08,
   "total_orders_7d_ma": 56.43
  },
  {
   "date_day": "2026-09-21",
   "total_orders": 61,
   "gross_revenue": 59737.11,
   "net_revenue": 26774.91,
   "average_order_value": 979.2968852459016,
   "fulfillment_rate": 0.5245901639344263,
   "cancellation_rate": 0.26229508196721313,
   "gross_revenue_7d_ma": 56022.42,
   "total_orders_7d_ma": 59.0
  },
  {
   "date_day": "2026-09-22",
   "total_orders": 54,
   "gross_revenue": 53430.07,
   "net_revenue": 35989.11,
   "average_order_value": 989.4457407407407,
   "fulfillment_rate": 0.7037037037037037,
   "cancellation_rate": 0.12962962962962962,
   "gross_revenue_7d_ma": 55478.41,
   "total_orders_7d_ma": 57.86
  },
  {
   "date_day": "2026-09-23",
   "total_orders": 51,
   "gross_revenue": 46451.28,
   "net_revenue": 24420.83,
   "average_order_value": 910.8094117647058,
   "fulfillment_rate": 0.5882352941176471,
   "cancellation_rate": 0.21568627450980393,
   "gross_revenue_7d_ma": 53104.86,
   "total_orders_7d_ma": 56.14
  },
  {
   "date_day": "2026-09-24",
   "total_orders": 51,
   "gross_revenue": 45643.83,
   "net_revenue": 23947.16,
   "average_order_value": 894.9770588235294,
   "fulfillment_rate": 0.5294117647058824,
   "cancellation_rate": 0.27450980392156865,
   "gross_revenue_7d_ma": 52325.31,
   "total_orders_7d_ma": 56.14
  },
  {
   "date_day": "2026-09-25",
   "total_orders": 48,
   "gross_revenue": 55702.87,
   "net_revenue": 35512.59,
   "average_order_value": 1160.4764583333333,
   "fulfillment_rate": 0.625,
   "cancellation_rate": 0.1875,
   "gross_revenue_7d_ma": 52491.59,
   "total_orders_7d_ma": 53.43
  },
  {
   "date_day": "2026-09-26",
   "total_orders": 63,
   "gross_revenue": 58409.59,
   "net_revenue": 33763.29,
   "average_order_value": 927.1363492063492,
   "fulfillment_rate": 0.6190476190476191,
   "cancellation_rate": 0.15873015873015872,
   "gross_revenue_7d_ma": 54772.28,
   "total_orders_7d_ma": 55.14
  },
  {
   "date_day": "2026-09-27",
   "total_orders": 54,
   "gross_revenue": 54601.78,
   "net_revenue": 29228.17,
   "average_order_value": 1011.1440740740741,
   "fulfillment_rate": 0.5185185185185185,
   "cancellation_rate": 0.25925925925925924,
   "gross_revenue_7d_ma": 53425.22,
   "total_orders_7d_ma": 54.57
  },
  {
   "date_day": "2026-09-28",
   "total_orders": 42,
   "gross_revenue": 36129.33,
   "net_revenue": 15975.81,
   "average_order_value": 860.2221428571429,
   "fulfillment_rate": 0.47619047619047616,
   "cancellation_rate": 0.38095238095238093,
   "gross_revenue_7d_ma": 50052.68,
   "total_orders_7d_ma": 51.86
  },
  {
   "date_day": "2026-09-29",
   "total_orders": 57,
   "gross_revenue": 50421.58,
   "net_revenue": 29034.59,
   "average_order_value": 884.5891228070176,
   "fulfillment_rate": 0.543859649122807,
   "cancellation_rate": 0.17543859649122806,
   "gross_revenue_7d_ma": 49622.89,
   "total_orders_7d_ma": 52.29
  },
  {
   "date_day": "2026-09-30",
   "total_orders": 55,
   "gross_revenue": 52965.16,
   "net_revenue": 23613.54,
   "average_order_value": 963.002909090909,
   "fulfillment_rate": 0.45454545454545453,
   "cancellation_rate": 0.3090909090909091,
   "gross_revenue_7d_ma": 50553.45,
   "total_orders_7d_ma": 52.86
  },
  {
   "date_day": "2026-10-01",
   "total_orders": 56,
   "gross_revenue": 50130.18,
   "net_revenue": 25722.19,
   "average_order_value": 895.1817857142858,
   "fulfillment_rate": 0.5357142857142857,
   "cancellation_rate": 0.21428571428571427,
   "gross_revenue_7d_ma": 51194.36,
   "total_orders_7d_ma": 53.57
  },
  {
   "date_day": "2026-10-02",
   "total_orders": 41,
   "gross_revenue": 37939.76,
   "net_revenue": 18494.93,
   "average_order_value": 925.36,
   "fulfillment_rate": 0.4878048780487805,
   "cancellation_rate": 0.17073170731707318,
   "gross_revenue_7d_ma": 48656.77,
   "total_orders_7d_ma": 52.57
  },
  {
   "date_day": "2026-10-03",
   "total_orders": 53,
   "gross_revenue": 48598.93,
   "net_revenue": 27016.71,
   "average_order_value": 916.9609433962264,
   "fulfillment_rate": 0.5094339622641509,
   "cancellation_rate": 0.2830188679245283,
   "gross_revenue_7d_ma": 47255.25,
   "total_orders_7d_ma": 51.14
  },
  {
   "date_day": "2026-10-04",
   "total_orders": 47,
   "gross_revenue": 42284.57,
   "net_revenue": 23581.79,
   "average_order_value": 899.6717021276596,
   "fulfillment_rate": 0.5319148936170213,
   "cancellation_rate": 0.23404255319148937,
   "gross_revenue_7d_ma": 45495.64,
   "total_orders_7d_ma": 50.14
  },
  {
   "date_day": "2026-10-05",
   "total_orders": 60,
   "gross_revenue": 49825.33,
   "net_revenue": 31728.83,
   "average_order_value": 830.4221666666666,
   "fulfillment_rate": 0.6,
   "cancellation_rate": 0.16666666666666666,
   "gross_revenue_7d_ma": 47452.22,
   "total_orders_7d_ma": 52.71
  },
  {
   "date_day": "2026-10-06",
   "total_orders": 47,
   "gross_revenue": 45152.23,
   "net_revenue": 29798.46,
   "average_order_value": 960.685744680851,
   "fulfillment_rate": 0.6170212765957447,
   "cancellation_rate": 0.14893617021276595,
   "gross_revenue_7d_ma": 46699.45,
   "total_orders_7d_ma": 51.29
  },
  {
   "date_day": "2026-10-07",
   "total_orders": 65,
   "gross_revenue": 64385.52,
   "net_revenue": 39690.05,
   "average_order_value": 990.5464615384616,
   "fulfillment_rate": 0.5846153846153846,
   "cancellation_rate": 0.2,
   "gross_revenue_7d_ma": 48330.93,
   "total_orders_7d_ma": 52.71
  },
  {
   "date_day": "2026-10-08",
   "total_orders": 30,
   "gross_revenue": 24325.95,
   "net_revenue": 12104.94,
   "average_order_value": 810.865,
   "fulfillment_rate": 0.4666666666666667,
   "cancellation_rate": 0.23333333333333334,
   "gross_revenue_7d_ma": 44644.61,
   "total_orders_7d_ma": 49.0
  },
  {
   "date_day": "2026-10-09",
   "total_orders": 60,
   "gross_revenue": 55777.96,
   "net_revenue": 36556.9,
   "average_order_value": 929.6326666666666,
   "fulfillment_rate": 0.7166666666666667,
   "cancellation_rate": 0.1,
   "gross_revenue_7d_ma": 47192.93,
   "total_orders_7d_ma": 51.71
  },
  {
   "date_day": "2026-10-10",
   "total_orders": 61,
   "gross_revenue": 61365.96,
   "net_revenue": 21509.66,
   "average_order_value": 1005.999344262295,
   "fulfillment_rate": 0.4098360655737705,
   "cancellation_rate": 0.29508196721311475,
   "gross_revenue_7d_ma": 49016.79,
   "total_orders_7d_ma": 52.86
  },
  {
   "date_day": "2026-10-11",
   "total_orders": 57,
   "gross_revenue": 57480.55,
   "net_revenue": 33850.45,
   "average_order_value": 1008.430701754386,
   "fulfillment_rate": 0.5263157894736842,
   "cancellation_rate": 0.21052631578947367,
   "gross_revenue_7d_ma": 51187.64,
   "total_orders_7d_ma": 54.29
  },
  {
   "date_day": "2026-10-12",
   "total_orders": 59,
   "gross_revenue": 56544.54,
   "net_revenue": 26348.16,
   "average_order_value": 958.382033898305,
   "fulfillment_rate": 0.4745762711864407,
   "cancellation_rate": 0.288135593220339,
   "gross_revenue_7d_ma": 52147.53,
   "total_orders_7d_ma": 54.14
  },
  {
   "date_day": "2026-10-13",
   "total_orders": 43,
   "gross_revenue": 44219.02,
   "net_revenue": 21886.31,
   "average_order_value": 1028.3493023255814,
   "fulfillment_rate": 0.46511627906976744,
   "cancellation_rate": 0.27906976744186046,
   "gross_revenue_7d_ma": 52014.21,
   "total_orders_7d_ma": 53.57
  },
  {
   "date_day": "2026-10-14",
   "total_orders": 53,
   "gross_revenue": 43538.46,
   "net_revenue": 28948.45,
   "average_order_value": 821.4803773584906,
   "fulfillment_rate": 0.660377358490566,
   "cancellation_rate": 0.1320754716981132,
   "gross_revenue_7d_ma": 49036.06,
   "total_orders_7d_ma": 51.86
  },
  {
   "date_day": "2026-10-15",
   "total_orders": 54,
   "gross_revenue": 54635.19,
   "net_revenue": 27184.79,
   "average_order_value": 1011.7627777777777,
   "fulfillment_rate": 0.5,
   "cancellation_rate": 0.35185185185185186,
   "gross_revenue_7d_ma": 53365.95,
   "total_orders_7d_ma": 55.29
  },
  {
   "date_day": "2026-10-16",
   "total_orders": 52,
   "gross_revenue": 48767.85,
   "net_revenue": 38090.98,
   "average_order_value": 937.8432692307692,
   "fulfillment_rate": 0.7884615384615384,
   "cancellation_rate": 0.09615384615384616,
   "gross_revenue_7d_ma": 52364.51,
   "total_orders_7d_ma": 54.14
  },
  {
   "date_day": "2026-10-17",
   "total_orders": 71,
   "gross_revenue": 76907.25,
   "net_revenue": 42025.84,
   "average_order_value": 1083.2007042253522,
   "fulfillment_rate": 0.5492957746478874,
   "cancellation_rate": 0.22535211267605634,
   "gross_revenue_7d_ma": 54584.69,
   "total_orders_7d_ma": 55.57
  },
  {
   "date_day": "2026-10-18",
   "total_orders": 68,
   "gross_revenue": 67095.44,
   "net_revenue": 46969.51,
   "average_order_value": 986.6976470588236,
   "fulfillment_rate": 0.6911764705882353,
   "cancellation_rate": 0.16176470588235295,
   "gross_revenue_7d_ma": 55958.25,
   "total_orders_7d_ma": 57.14
  },
  {
   "date_day": "2026-10-19",
   "total_orders": 51,
   "gross_revenue": 43358.6,
   "net_revenue": 23558.24,
   "average_order_value": 850.1686274509804,
   "fulfillment_rate": 0.5490196078431373,
   "cancellation_rate": 0.2549019607843137,
   "gross_revenue_7d_ma": 54074.54,
   "total_orders_7d_ma": 56.0
  },
  {
   "date_day": "2026-10-20",
   "total_orders": 51,
   "gross_revenue": 54125.65,
   "net_revenue": 32557.84,
   "average_order_value": 1061.2872549019608,
   "fulfillment_rate": 0.5098039215686274,
   "cancellation_rate": 0.1568627450980392,
   "gross_revenue_7d_ma": 55489.78,
   "total_orders_7d_ma": 57.14
  },
  {
   "date_day": "2026-10-21",
   "total_orders": 53,
   "gross_revenue": 51356.79,
   "net_revenue": 32995.38,
   "average_order_value": 968.9960377358491,
   "fulfillment_rate": 0.6037735849056604,
   "cancellation_rate": 0.1509433962264151,
   "gross_revenue_7d_ma": 56606.68,
   "total_orders_7d_ma": 57.14
  },
  {
   "date_day": "2026-10-22",
   "total_orders": 40,
   "gross_revenue": 44921.43,
   "net_revenue": 26452.67,
   "average_order_value": 1123.03575,
   "fulfillment_rate": 0.625,
   "cancellation_rate": 0.2,
   "gross_revenue_7d_ma": 55219.0,
   "total_orders_7d_ma": 55.14
  },
  {
   "date_day": "2026-10-23",
   "total_orders": 63,
   "gross_revenue": 58126.68,
   "net_revenue": 37982.0,
   "average_order_value": 922.6457142857142,
   "fulfillment_rate": 0.6031746031746031,
   "cancellation_rate": 0.14285714285714285,
   "gross_revenue_7d_ma": 56555.98,
   "total_orders_7d_ma": 56.71
  },
  {
   "date_day": "2026-10-24",
   "total_orders": 27,
   "gross_revenue": 25877.68,
   "net_revenue": 20426.42,
   "average_order_value": 958.4325925925926,
   "fulfillment_rate": 0.7037037037037037,
   "cancellation_rate": 0.07407407407407407,
   "gross_revenue_7d_ma": 49266.04,
   "total_orders_7d_ma": 50.43
  }
 ],
 "windows": {
  "7": {
   "metrics": {
    "current": {
     "orders": 353,
     "revenue": 344862.27,
     "aov": 976.9469405099151,
     "fulfillment_rate": 0.6090651558073654,
     "customers": 255
    },
    "previous": {
     "orders": 389,
     "revenue": 382092.86,
     "aov": 982.2438560411312,
     "fulfillment_rate": 0.5655526992287918,
     "customers": 272
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
     "orders": 41,
     "revenue": 35736.33
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
     "orders": 29,
     "revenue": 22153.07
    }
   ],
   "segments": [
    {
     "label": "loyal_customer",
     "orders": 331,
     "revenue": 323695.81,
     "customers": 235
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
     "orders": 52,
     "revenue": 47155.19,
     "aov": 906.8305769230769
    },
    {
     "label": "CA",
     "orders": 50,
     "revenue": 43447.66,
     "aov": 868.9532
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
     "avg_days": 3.840909090909091
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
     "avg_days": 3.8275862068965516
    },
    {
     "label": "DHL",
     "shipments": 28,
     "on_time_rate": 0.5,
     "avg_days": 3.857142857142857
    }
   ],
   "payment": [
    {
     "label": "credit_card",
     "orders": 151,
     "revenue": 148803.38
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
     "orders": 62,
     "revenue": 54399.83
    }
   ]
  },
  "30": {
   "metrics": {
    "current": {
     "orders": 1581,
     "revenue": 1514971.83,
     "aov": 958.2364516129032,
     "fulfillment_rate": 0.5660974067046173,
     "customers": 470
    },
    "previous": {
     "orders": 1630,
     "revenue": 1592932.39,
     "aov": 977.2591349693251,
     "fulfillment_rate": 0.5674846625766872,
     "customers": 487
    }
   },
   "status": [
    {
     "label": "delivered",
     "orders": 711,
     "revenue": 693920.84
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
     "orders": 1480,
     "revenue": 1422563.2,
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
     "orders": 205,
     "revenue": 206446.36,
     "aov": 1007.0554146341464
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
     "label": "FedEx",
     "shipments": 153,
     "on_time_rate": 0.5490196078431373,
     "avg_days": 3.738562091503268
    },
    {
     "label": "DHL",
     "shipments": 152,
     "on_time_rate": 0.47368421052631576,
     "avg_days": 4.0
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
     "avg_days": 3.902097902097902
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
     "orders": 310,
     "revenue": 314582.83
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
     "orders": 4871,
     "revenue": 4710252.54,
     "aov": 966.9990843769247,
     "fulfillment_rate": 0.5719564771094231,
     "customers": 500
    },
    "previous": {
     "orders": 25,
     "revenue": 24402.84,
     "aov": 976.1136,
     "fulfillment_rate": 0.44,
     "customers": 25
    }
   },
   "status": [
    {
     "label": "delivered",
     "orders": 2222,
     "revenue": 2185712.18
    },
    {
     "label": "shipped",
     "orders": 564,
     "revenue": 536495.17
    },
    {
     "label": "cancelled",
     "orders": 547,
     "revenue": 537080.59
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
     "orders": 4413,
     "revenue": 4269281.5,
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
     "orders": 1522,
     "revenue": 1462145.17,
     "aov": 960.673567674113
    },
    {
     "label": "DE",
     "orders": 744,
     "revenue": 729534.91,
     "aov": 980.5576747311828
    },
    {
     "label": "AU",
     "orders": 745,
     "revenue": 710054.65,
     "aov": 953.0934899328859
    },
    {
     "label": "FR",
     "orders": 656,
     "revenue": 640944.72,
     "aov": 977.0498780487804
    },
    {
     "label": "CA",
     "orders": 614,
     "revenue": 601571.22,
     "aov": 979.757687296417
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
     "avg_days": 3.908333333333333
    },
    {
     "label": "UPS",
     "shipments": 480,
     "on_time_rate": 0.48333333333333334,
     "avg_days": 4.010416666666667
    },
    {
     "label": "USPS",
     "shipments": 473,
     "on_time_rate": 0.5052854122621564,
     "avg_days": 3.9323467230443976
    },
    {
     "label": "DHL",
     "shipments": 457,
     "on_time_rate": 0.48358862144420134,
     "avg_days": 4.035010940919038
    }
   ],
   "payment": [
    {
     "label": "credit_card",
     "orders": 1990,
     "revenue": 1900368.31
    },
    {
     "label": "paypal",
     "orders": 978,
     "revenue": 979450.3
    },
    {
     "label": "bank_transfer",
     "orders": 956,
     "revenue": 913918.28
    },
    {
     "label": "apple_pay",
     "orders": 947,
     "revenue": 916515.65
    }
   ]
  }
 }
};
