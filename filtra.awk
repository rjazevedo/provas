BEGIN { FS = ","; OFS = "," }
{gsub("/home/dados/provas/","",$5); print}
