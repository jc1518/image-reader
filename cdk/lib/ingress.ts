import { Construct } from "constructs";
import * as cognito from "aws-cdk-lib/aws-cognito";
import * as acm from "aws-cdk-lib/aws-certificatemanager";
import * as ec2 from "aws-cdk-lib/aws-ec2";
import * as elbv2 from "aws-cdk-lib/aws-elasticloadbalancingv2";
import * as ecs from "aws-cdk-lib/aws-ecs";
import * as route53 from "aws-cdk-lib/aws-route53";
import {
  CfnWebACL,
  CfnWebACLAssociation,
  CfnIPSet,
} from "aws-cdk-lib/aws-wafv2";
import { AuthenticateCognitoAction } from "aws-cdk-lib/aws-elasticloadbalancingv2-actions";

export interface AppIngressProps {
  vpc: ec2.IVpc;
  domain: string;
  host: string;
  zoneId: string;
  allowedIps: string[];
  ecsService: ecs.FargateService;
}

export class AppIngress extends Construct {
  public readonly loadBalancer: elbv2.IApplicationLoadBalancer;

  constructor(scope: Construct, id: string, props: AppIngressProps) {
    super(scope, id);

    const ipSet = new CfnIPSet(this, "AppIPSet", {
      addresses: props.allowedIps,
      ipAddressVersion: "IPV4",
      scope: "REGIONAL",
    });

    const webAcl = new CfnWebACL(this, "AppWebACL", {
      name: "image-reader-web-acl",
      scope: "REGIONAL",
      defaultAction: { block: {} },
      visibilityConfig: {
        cloudWatchMetricsEnabled: true,
        metricName: "App-web-acl-blocked",
        sampledRequestsEnabled: true,
      },
      rules: [
        {
          name: "image-reader-web-acl-allowed",
          priority: 1,
          action: { allow: {} },
          statement: { ipSetReferenceStatement: { arn: ipSet.attrArn } },
          visibilityConfig: {
            cloudWatchMetricsEnabled: true,
            metricName: "image-reader-web-acl-allowed",
            sampledRequestsEnabled: true,
          },
        },
      ],
    });

    const userPool = new cognito.UserPool(this, "AppUserPool", {
      userPoolName: "image-reader-user-pool",
      selfSignUpEnabled: false,
      signInAliases: {
        email: true,
        username: false,
        phone: false,
      },
    });

    const userPoolDomain = userPool.addDomain("AppDomain", {
      cognitoDomain: {
        domainPrefix: "image-reader",
      },
    });

    const appClient = userPool.addClient("AppAppClient", {
      generateSecret: true,
      authFlows: { userSrp: true },
      oAuth: {
        flows: { authorizationCodeGrant: true },
        callbackUrls: [
          `https://${props.host}.${props.domain}/oauth2/idpresponse`,
        ],
        logoutUrls: [`https://${props.host}.${props.domain}/logout`],
      },
    });

    const loadBalancerSecurityGroup = new ec2.SecurityGroup(
      this,
      "AppLoadBalancerSecurityGroup",
      {
        vpc: props.vpc,
        allowAllOutbound: true,
        securityGroupName: "image-reader-load-balancer-security-group",
      }
    );

    loadBalancerSecurityGroup.addIngressRule(
      ec2.Peer.anyIpv4(),
      ec2.Port.tcp(443),
      "HTTPS"
    );

    this.loadBalancer = new elbv2.ApplicationLoadBalancer(
      this,
      "AppLoadBalancer",
      {
        vpc: props.vpc,
        internetFacing: true,
        securityGroup: loadBalancerSecurityGroup,
      }
    );

    const wafAssociation = new CfnWebACLAssociation(this, "AppWafAssociation", {
      resourceArn: this.loadBalancer.loadBalancerArn,
      webAclArn: webAcl.attrArn,
    });

    const certificate = new acm.Certificate(this, "AppCertificate", {
      domainName: `${props.host}.${props.domain}`,
      validation: acm.CertificateValidation.fromDns(),
    });

    const targetGroup = new elbv2.ApplicationTargetGroup(
      this,
      "AppTargetGroup",
      {
        port: 8501,
        protocol: elbv2.ApplicationProtocol.HTTP,
        targetType: elbv2.TargetType.IP,
        vpc: props.vpc,
      }
    );

    targetGroup.addTarget(props.ecsService);
    targetGroup.configureHealthCheck({
      path: "/_stcore/health",
      protocol: elbv2.Protocol.HTTP,
      port: "8501",
    });

    this.loadBalancer.addListener("AppListener", {
      port: 443,
      certificates: [certificate],
      defaultAction: new AuthenticateCognitoAction({
        userPool: userPool,
        userPoolClient: appClient,
        userPoolDomain: userPoolDomain,
        next: elbv2.ListenerAction.forward([targetGroup]),
      }),
    });

    const zone = route53.HostedZone.fromHostedZoneAttributes(
      this,
      "AppHostedZone",
      {
        zoneName: props.domain,
        hostedZoneId: props.zoneId,
      }
    );

    const dns = new route53.CnameRecord(this, "AppCnameRecord", {
      recordName: props.host,
      zone: zone,
      domainName: this.loadBalancer.loadBalancerDnsName,
    });
  }
}
