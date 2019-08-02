for repo in `cat repos.out`; do
  repo_count=$(($repo_count + 1))
  sizes=`aws ecr describe-images --repository-name $repo \
  --query "imageDetails[*].imageSizeInBytes" \
  | egrep -v '\[|\]' | \
  sed 's/,//' | \
  sed 's/^[[:space:]]*//g'`

  subtotal=0
  for size in $sizes; do
    repo_image_count=$(($repo_image_count + 1))
    image_count=$(($image_count + 1))
    subtotal=$(($subtotal + $size))
    total=$(($total + $size))
  done
  subtotalGB=$(($subtotal/1024/1024))
  echo "$repo $repo_image_count images $subtotalGB MB"

done
totalGB=$(($total/1024/1024/1024))
echo ""
echo "=========================================================="
echo "TOTALS"
echo "=========================================================="
echo "$repo_count repositories"
echo "$image_count images"
echo "$totalGB GB storage"