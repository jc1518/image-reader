import { Construct } from "constructs";
import * as cdk from "aws-cdk-lib";
import * as ecs from "aws-cdk-lib/aws-ecs";
import * as ec2 from "aws-cdk-lib/aws-ec2";
import * as iam from "aws-cdk-lib/aws-iam";
import * as efs from "aws-cdk-lib/aws-efs";

export interface AppEcsProps {
  name: string;
  vpc: ec2.IVpc;
  fileSystem: efs.IFileSystem;
  accessPoint: efs.IAccessPoint;
}

export class AppEcs extends Construct {
  public readonly service: ecs.FargateService;

  constructor(scope: Construct, id: string, props: AppEcsProps) {
    super(scope, id);

    const cluster = new ecs.Cluster(this, "AppCluster", {
      clusterName: props.name,
      vpc: props.vpc,
      containerInsights: true,
      enableFargateCapacityProviders: true,
    });

    const taskDefinition = new ecs.FargateTaskDefinition(
      this,
      "AppTaskDefinition",
      {
        memoryLimitMiB: 1024,
        cpu: 512,
        ephemeralStorageGiB: 80,
      }
    );

    taskDefinition.addVolume({
      name: "data",
      efsVolumeConfiguration: {
        fileSystemId: props.fileSystem.fileSystemId,
        transitEncryption: "ENABLED",
        authorizationConfig: {
          accessPointId: props.accessPoint.accessPointId,
          iam: "ENABLED",
        },
      },
    });

    const containerDefinition = taskDefinition.addContainer("AppContainer", {
      image: ecs.ContainerImage.fromAsset("../image-reader"),
      containerName: "image-reader-container",
      logging: ecs.LogDriver.awsLogs({
        streamPrefix: "image-reader",
        logRetention: 30,
      }),
      portMappings: [{ containerPort: 8501, hostPort: 8501 }],
      essential: true,
    });
    containerDefinition.addMountPoints({
      containerPath: "/image-reader/data",
      readOnly: false,
      sourceVolume: "data",
    });

    const taskRole = taskDefinition.taskRole;
    taskRole.addToPrincipalPolicy(
      new iam.PolicyStatement({
        actions: ["bedrock:invoke*"],
        resources: ["*"],
      })
    );
    taskRole.addToPrincipalPolicy(
      new iam.PolicyStatement({
        actions: [
          "elasticfilesystem:ClientRootAccess",
          "elasticfilesystem:ClientWrite",
          "elasticfilesystem:ClientMount",
          "elasticfilesystem:DescribeMountTargets",
        ],
        resources: [props.fileSystem.fileSystemArn],
      })
    );
    taskRole.addToPrincipalPolicy(
      new iam.PolicyStatement({
        actions: ["ec2:DescribeAvailabilityZones"],
        resources: ["*"],
      })
    );

    const serviceSecurityGroup = new ec2.SecurityGroup(
      this,
      "AppServiceSecurityGroup",
      {
        vpc: props.vpc,
        allowAllOutbound: true,
        securityGroupName: "app-service-sg",
      }
    );
    serviceSecurityGroup.addIngressRule(
      ec2.Peer.ipv4(props.vpc.vpcCidrBlock),
      ec2.Port.tcp(8501),
      "Streamlit"
    );

    this.service = new ecs.FargateService(this, "AppService", {
      cluster: cluster,
      desiredCount: 1,
      taskDefinition: taskDefinition,
      healthCheckGracePeriod: cdk.Duration.seconds(300),
      capacityProviderStrategies: [
        {
          capacityProvider: "FARGATE_SPOT",
          weight: 2,
        },
        {
          capacityProvider: "FARGATE",
          weight: 1,
        },
      ],
    });
  }
}
