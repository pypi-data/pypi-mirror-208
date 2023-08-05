#! /usr/bin/env bash
# build the zipped image files for ingestion into google books

# ------------      functions  ---------------

function close_log_dip() {
  dip_log_id="$1"
  comment="$2"
  rc="$3"

  end_time=$(date +'%Y-%m-%d %R:%S')
  # Can lose -d $DB_CONFIG
  # Also, dont need -w or -a. Just the id and the rc  will do
  #   log_dip -e "${end_time}" -r "${rc}" -a "SINGLE_ARCHIVE" -w "${rid}" -i "${ia_dip_log_id}" -c "${comment}"
  log_dip $NOLOG -e "${end_time}" -r "${rc}" -i "${dip_log_id}" -c "${comment}"
}

function die() {
    endTime=$(date +'%Y-%m-%d %R:%S')
  log_dip -d prod:~/.drsBatch.config -e "${endTime}" -r $ziprc -i $googleBooksLogDipID
  if [[ $2 == 0 ]]; then
    exit $2
  fi
  snsFailsMessageString=$(printf "\nThe following work could not be prepared for Google Books \n%1s\n\n%2s\n Returned with an Exit Value of%3s\n" \
    "$(echo ${rid})" \
    "$(echo $1)" \
    "$(echo $2)")
  snsMessage=$(printf "%s\n%s\n" "$(date --rfc-email)" "${snsFailsMessageString}")
  if [[ -n $DEBUG_SYNC ]]; then
    echo "----------  $DEBUG_SYNC ------------"
    if [[ -n $AO_AWS_SNS_TOPIC_ARN ]]; then
      echo "sending to topic  $AO_AWS_SNS_TOPIC_ARN"
    else
      echo "No send to SNS"
    fi
    echo "${snsMessage}"
    echo "----------  $DEBUG_SYNC ------------"

  fi
  if [[ -n $AO_AWS_SNS_TOPIC_ARN ]]; then
    snsSubject="Google Books Build Failed Report"
    aws sns publish --topic-arn $AO_AWS_SNS_TOPIC_ARN \
      --subject "${snsSubject}"
    --message "${snsMessage}"
  else
    echo "${snsMessage}"
  fi

  exit $2
}

# -----------    end functions ----------------
# -----------    main          ----------------
ME=$0
ME_DIR=$(dirname ${ME})
EXCLUDE_FILE=${ME_DIR}/hiddenexclude.lst
USAGE="USAGE:  ${ME} pathToSources outputPath"
srcDir=${1:?${USAGE}}
workDir=$(readlink -f ${2:?${USAGE}})

rid=$(basename $srcDir)

if [ ! -d $srcDir ]; then
  errMessage="$srcDir not found"
  echo ${errMessage}
  #changing email message here to not send local paths over email.
  errMessage="$rid not found"
  evl=1
  die "$errMessage" $evl
fi

image_dir=$workDir/IMAGES
beginTime=$(date +'%Y-%m-%d %R:%S')
googleBooksLogDipID=$(log_dip -b "${beginTime}" -a "GOOGLE_BOOKS" -w "${rid}" "${srcDir}" "${workDir}")
if [ -d $srcDir/images ]; then
  export ziprc=$((0))
  for rid_image_Src in $srcDir/images/$rid*; do
    IMGR=$(basename $rid_image_Src)
    zipfile=${IMGR}.zip
    #move images to working dir
    rsync -ai --exclude "*.json" $rid_image_Src $workDir/IMAGES/
    #rename images to 0000XXXX.tif format

    [ -d $workDir/IMAGES/$IMGR ] && {
      cd $image_dir/$IMGR
      image_number=1
      for file in $(ls -v); do
        #7 leading digits is google's page numbering standard
        image_number_zero_padded=$(printf "%07d" $image_number)
        file_ext="${file##*.}"
        new_filename=${image_number_zero_padded}.${file_ext}
        #   echo "$file-->$new_filename"
        mv -nv $file $new_filename
        ((image_number++))
      done
      cd $image_dir
      zip -q -rm $zipfile $IMGR -x@${EXCLUDE_FILE} -x "*.json"
      export ziprc=$((ziprc + $?))
      errMessage=$(printf "Zip error %s during creation\n" $ziprc)
      close_log_dip "$googleBooksLogDipID" "$errMessage" "$ziprc"
      cd $workDir
    }
  done
else
  echo $srcDir"/images not found"
fi
errMessage=""
evl=0
close_log_dip "$googleBooksLogDipID" "$errMessage" "$evl"
die "$errMessage" $evl

