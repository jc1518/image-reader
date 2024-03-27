import { Construct } from "constructs";
import * as efs from "aws-cdk-lib/aws-efs";
import * as ec2 from "aws-cdk-lib/aws-ec2";

export interface AppEfsProps {
  name: string;
  vpc: ec2.IVpc;
  accessPointPath: string;
}

export class AppEfs extends Construct {
  public readonly fileSystem: efs.FileSystem;
  public readonly accessPoint: efs.AccessPoint;

  constructor(scope: Construct, id: string, props: AppEfsProps) {
    super(scope, id);

    this.fileSystem = new efs.FileSystem(this, "Efs", {
      fileSystemName: props.name,
      vpc: props.vpc,
      encrypted: true,
      enableAutomaticBackups: true,
      performanceMode: efs.PerformanceMode.GENERAL_PURPOSE,
      throughputMode: efs.ThroughputMode.BURSTING,
      vpcSubnets: { subnetType: ec2.SubnetType.PRIVATE_WITH_EGRESS },
    });

    this.fileSystem.connections.allowDefaultPortFrom(
      ec2.Peer.ipv4(props.vpc.vpcCidrBlock)
    );

    this.accessPoint = this.fileSystem.addAccessPoint("AppEfsAccessPoint", {
      path: props.accessPointPath,
      createAcl: {
        ownerGid: "1001",
        ownerUid: "1001",
        permissions: "750",
      },
      posixUser: {
        gid: "1001",
        uid: "1001",
      },
    });
  }
}
