#!/bin/sh
if [ ! -d ./node_modules ]; then
  npm install
fi

if [ ! -d /cache/node_modules ]; then
  echo "Bind mounting node_modules from cache"
  echo "This will take a few minutes on the first run"
  cp -r ./node_modules /cache
fi

npm run dev
