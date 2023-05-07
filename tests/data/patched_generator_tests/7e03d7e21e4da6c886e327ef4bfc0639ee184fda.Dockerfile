#  ベースイメージの設定
FROM ubuntu-test-stand

# Nginx のインストール
RUN apt-get -y update && apt-get -y upgrade 
RUN apt-get -y install nginx

#  ポート指定
EXPOSE 80

# Web コンテンツの配置
ONBUILD ADD website.tar /var/www/html/

# Nginx の実行
CMD ["nginx", "-g", "daemon off;"]
