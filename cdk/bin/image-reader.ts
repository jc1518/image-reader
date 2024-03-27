#!/usr/bin/env node
import "source-map-support/register";
import * as path from "path";
import { loadConfig } from "../lib/utils";
import * as cdk from "aws-cdk-lib";
import { AppConfigProps, AppStack } from "../lib/app-stack";

const CONFIG_FILE = process.env.IMAGE_READER_CONFIG_FILE
  ? process.env.IMAGE_READER_CONFIG_FILE
  : path.join(__dirname, "../config.yaml");
const loadResult = loadConfig(CONFIG_FILE);

if (!loadResult.success) {
  console.error(loadResult.message);
  process.exit(1);
}

const app = new cdk.App();

const appConfig = JSON.parse(loadResult.data) as AppConfigProps;

const env = {
  account: process.env.CDK_DEFAULT_ACCOUNT,
  region: process.env.CDK_DEFAULT_REGION,
};

const appStack = new AppStack(app, "ImageReaderStack", appConfig, {
  env: env,
});

cdk.Tags.of(appStack).add("Application", "image-reader");
