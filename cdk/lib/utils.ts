import * as fs from "fs";
import * as yaml from "js-yaml";

type Result = {
  success: boolean;
  message: string;
  data: string;
};

// Read config file
export function readConfigFile(configFile: string): string {
  try {
    const config = yaml.load(fs.readFileSync(configFile, "utf8"));
    return JSON.stringify(config);
  } catch (e) {
    console.error("Failed to load config file.");
    throw new Error(JSON.stringify(e));
  }
}

// Load config file if exists
export function loadConfig(configFile: string): Result {
  if (fs.existsSync(configFile)) {
    const config = readConfigFile(configFile);
    return {
      success: true,
      message: `Config file ${configFile} is found.`,
      data: config,
    };
  } else {
    return {
      success: false,
      message: `Config file ${configFile} is missing.`,
      data: "",
    };
  }
}
