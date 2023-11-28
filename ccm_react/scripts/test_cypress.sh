#!/bin/bash
cd ../
uvicorn ccm_api.main:app & uvicorn_pid=$!
cd ./ccm_react
npm run dev & npm_pid=$!
npx cypress run
kill $uvicorn_pid || true
kill $npm_pid || true
