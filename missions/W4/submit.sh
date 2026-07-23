#!/bin/bash

echo "Submitting TLC trip analysis Spark job..."

docker exec spark-master spark-submit \
  --master spark://spark-master:7077 \
  --driver-memory 1g \
  --executor-memory 1g \
  /opt/spark/jobs/analysis.py \
  --311-path "/opt/spark/data/raw/311_Service_Requests_from_2020_to_Present_20260723.csv" \
  --trips-path "/opt/spark/data/raw/fhvhv_tripdata_2025-*.parquet" \
  --output-dir /opt/spark/data/output

exit_code=$?
if [ $exit_code -eq 0 ]; then
  echo "Job execution completed!"
else
  echo "Job execution FAILED (exit code $exit_code)"
fi
exit $exit_code
