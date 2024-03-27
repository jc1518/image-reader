import * as cdk from "aws-cdk-lib";
import { Construct } from "constructs";
import { AppVpcProps, AppVpc } from "./vpc";
import { AppEfsProps, AppEfs } from "./efs";
import { AppEcsProps as AppEcsProps, AppEcs as AppEcs } from "./ecs";
import { AppIngressProps, AppIngress } from "./ingress";

export interface AppConfigProps {
  name: string;
  cidr: string;
  publicCidrMask: number;
  privateCidrMask: number;
  maxAzs: number;
  natGateways: number;
  domain: string;
  host: string;
  zoneId: string;
  allowedIps: string[];
}

export class AppStack extends cdk.Stack {
  constructor(
    scope: Construct,
    id: string,
    config: AppConfigProps,
    props?: cdk.StackProps
  ) {
    super(scope, id, props);

    // Prefix
    const name = config.name;
    // Vpc config
    const cidr = config.cidr;
    const maxAz = config.maxAzs;
    const natGateways = config.natGateways;
    const privateCidrMask = config.privateCidrMask;
    const publicCidrMask = config.publicCidrMask;
    // Ingress config
    const domain = config.domain;
    const host = config.host;
    const zoneId = config.zoneId;
    const allowedIps = config.allowedIps;

    const vpcInfo: AppVpcProps = {
      name: `${name}-vpc`,
      cidr: cidr,
      publicCidrMask: publicCidrMask,
      privateCidrMask: privateCidrMask,
      maxAzs: maxAz,
      natGateways: natGateways,
    };

    const appVpc = new AppVpc(this, "AppVpc", vpcInfo);

    const efsInfo: AppEfsProps = {
      name: `${name}-efs`,
      vpc: appVpc.vpc,
      accessPointPath: "/app-data",
    };

    const appEfs = new AppEfs(this, "AppEfs", efsInfo);

    const ecsInfo: AppEcsProps = {
      name: `${name}-ecs`,
      vpc: appVpc.vpc,
      fileSystem: appEfs.fileSystem,
      accessPoint: appEfs.accessPoint,
    };

    const appEcs = new AppEcs(this, "AppEcs", ecsInfo);

    const ingressInfo: AppIngressProps = {
      vpc: appVpc.vpc,
      domain: domain,
      host: host,
      zoneId: zoneId,
      allowedIps: allowedIps,
      ecsService: appEcs.service,
    };

    const appIngress = new AppIngress(this, "AppIngress", ingressInfo);
  }
}
