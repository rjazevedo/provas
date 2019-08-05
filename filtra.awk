BEGIN { FS = ","; OFS = "," }
NR > 1 {gsub("/home/dados/provas/","",$5); print}
