BEGIN { FS = "," }
$0 !~ /em\ branco/ {print}
