bash scenarios.sh > test_output.log
cmp --silent test_output.log correct_output.log || echo "FAIL Test outputs are different"
