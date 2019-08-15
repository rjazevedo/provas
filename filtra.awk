BEGIN { FS = ","; OFS = "," }
{gsub("/home/provas/dados/","",$5); print}
