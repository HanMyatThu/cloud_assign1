#!/bin/bash

# files path for load balancer, scaling controller, and logger
BALANCER_PATH="/home/vagrant/files/balancer.py"
SCALER_PATH="/home/vagrant/files/scaling_controller.py"
LOGGER_PATH="/home/vagrant/files/logger.py"

# Load Balancer
echo "Starting Load Balancer!"
nohup python3 $BALANCER_PATH > balancer.out 2>&1 &

# Scaling Controller!
echo "Starting Scaling Controller! Default is algo 1"
nohup python3 $SCALER_PATH --algo 1 > scaler.out 2>&1 &

# Logger function!
echo "Starting Logger!"
nohup python3 $LOGGER_PATH > logger.out 2>&1 &

# Done
echo "All Done!"
