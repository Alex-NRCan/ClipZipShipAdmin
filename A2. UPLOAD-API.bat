@echo off

SET AWS_ACCESS_KEY_ID=ASIASBBECZZFQYFN4KMN
SET AWS_SECRET_ACCESS_KEY=KlVrH/Tfab+9XlC1Sw94AMZx2R6QkiAazP6McxO3
SET AWS_SESSION_TOKEN=IQoJb3JpZ2luX2VjEE4aDGNhLWNlbnRyYWwtMSJHMEUCIQCHH+YnK7X1btse3hxs0cuf55t8Hmn2acEIygvMOfgQrgIgaMk0wpPw/ETvmgtwuXE+MPgxmUqwPPrxrcRvBnCKNOcquAMIp///////////ARACGgwxMzk2NjIxMTg0NzUiDJbK3NmG+xn06Whh2yqMAzZWtTwa5VbUCB9PCt0jVWxLGGCzJWG4PAGgC1bZJoWvhyvPL/YeYuf8gXmZ8RBxdvw1gCwwuJS1zGxaogsw6LH1ONsbA7QsC+LqkUt0S/8u2Ttt9sO3xZENXBrTlym/ATqJVWoL+6YTykOmDMEpR/4YvJa6YXBs3bI4ZALGWUr3mHw+1TkgvVw/ag/jD53mII6p4lKVVNd1NXRflVYBxFlz5jj1nVG0xQJEyfmNrCMnwWCbKbl+K2b+cs7JF8n8KmJrf0j8f4ugXOI+VTcdAMPEtc7IZWyHM0xS9G78r62+LU2Geai7Nj+LLSllqQFdMXfWvCWrGfFtnafYUNrANhx0uesliVTHmZ18/ON3LhL8a5++Efv1bc6vUdeP4/tbxV/Xx+Nl+Uo25vQ/lHV7NSdnZV5GQtdt6yVx2A/3lbAagaLxTfdW2Wq09iw0aUmsr/2joJG2aH0gv2yUf9jCpJuFg/lPFgXknxej0FeqwhVOp3PeVfpIX8J093k9Qzu0PEl5++zSwoR+JD1WhDD1xeOQBjqmAcwwMHg+FqRJ0ji/1rgoBSW4nxNvy6tIYaeFkhFl7JilgHGS/Hq2OZCsolTnmy8OEPrZQUVftaL8kCkKJSapR700kwi8EDv92w0L/PaiKjtZn+eOJ4OBIUrf/LNDCQj25VONMflk4B77ypw8+SdLIYDAa/9Yj3gsqExdcIx7o4XnAl7cwJCmZXhuRtads5+KEFskx5GGUu95fV0Zfh+amYsyvVuYOTM=

: path of FME Server Backup File
set IN_FILE="C:\Users\alexroy\Desktop\Python\quality-api"

: path of Backup File s3 Upload Process Log File
set LOG_FILE="C:\Users\alexroy\Desktop\Python\quality-api.log"

: path of AWS CLI Executable
set AWSCLI="C:\Program Files\Amazon\AWSCLIV2\aws.exe"

: Set s3 Bucket Paths
set AWSBUCKET="s3://quality-bucket/docker-images/"

: upload the Backup Files to the AWS s3 Bucket
%AWSCLI% s3 cp %IN_FILE% %AWSBUCKET% --no-verify-ssl --cli-read-timeout 0 --debug 2>%LOG_FILE%
: PAUSE
