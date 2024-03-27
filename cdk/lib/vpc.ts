import { Construct } from "constructs";
import * as ec2 from "aws-cdk-lib/aws-ec2";
import * as cdk from "aws-cdk-lib";

export interface AppVpcProps {
  name: string;
  cidr: string;
  publicCidrMask: number;
  privateCidrMask: number;
  maxAzs: number;
  natGateways: number;
}

export class AppVpc extends Construct {
  public readonly vpc: ec2.IVpc;

  constructor(scope: Construct, id: string, props: AppVpcProps) {
    super(scope, id);

    const vpc = new ec2.Vpc(this, "Vpc", {
      vpcName: props.name,
      ipAddresses: ec2.IpAddresses.cidr(props.cidr),
      maxAzs: props.maxAzs,
      natGateways: props.natGateways,
      subnetConfiguration: [
        {
          cidrMask: props.publicCidrMask,
          name: "public",
          subnetType: ec2.SubnetType.PUBLIC,
        },
        {
          cidrMask: props.privateCidrMask,
          name: "private",
          subnetType: ec2.SubnetType.PRIVATE_WITH_EGRESS,
        },
      ],
    });

    this.vpc = vpc;
  }
}
