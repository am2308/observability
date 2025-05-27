import boto3
import botocore.config
import json
import requests
import subprocess
import os
from datetime import datetime

# Slack webhook URL
SLACK_WEBHOOK_URL = "https://hooks.slack.com/services/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"

# EKS cluster details
EKS_CLUSTER_NAME = "amcdemo"
EKS_REGION = "ap-south-1"
DEPLOYMENT_NAME = "result"
CONTAINER_NAME = "result"
NEW_IMAGE = "dockersamples/examplevotingapp_result"

def send_to_slack(message):
    """Send a message to Slack"""
    response = requests.post(SLACK_WEBHOOK_URL, json={"text": message})
    response.raise_for_status()

def blog_generate_using_bedrock():
    prompt = """Debug steps to rectify cpu utilization alert triggered by prometheus for my application deployed in EKS"""

    body = {
        "prompt": prompt,
        "max_gen_len": 512,
        "temperature": 0.5,
        "top_p": 0.9
    }

    try:
        bedrock = boto3.client("bedrock-runtime", region_name="us-east-1",
                               config=botocore.config.Config(read_timeout=300, retries={'max_attempts': 3}))
        response = bedrock.invoke_model(body=json.dumps(body), modelId="meta.llama3-70b-instruct-v1:0")

        response_content = response.get('body').read()
        response_data = json.loads(response_content)
        print(response_data)
        blog_details = response_data['generation']
        return blog_details
    except Exception as e:
        print(f"Error generating the blog: {e}")
        return ""

def update_eks_deployment():
    """Update the EKS deployment using kubectl set image"""
    try:
        # Set up kubeconfig for EKS
        kubeconfig = f"""
apiVersion: v1
clusters:
- cluster:
    certificate-authority-data: LS0tLS1CRUdJTiBDRVJUSUZJQ0FURS0tLS0tCk1JSURCVENDQWUyZ0F3SUJBZ0lJZXZkZDhLb1I4U3d3RFFZSktvWklodmNOQVFFTEJRQXdGVEVUTUJFR0ExVUUKQXhNS2EzVmlaWEp1WlhSbGN6QWVGdzB5TkRBNU1qSXhNelV3TWpCYUZ3MHpOREE1TWpBeE16VTFNakJhTUJVeApFekFSQmdOVkJBTVRDbXQxWW1WeWJtVjBaWE13Z2dFaU1BMEdDU3FHU0liM0RRRUJBUVVBQTRJQkR3QXdnZ0VLCkFvSUJBUUN5SlU0aWJmQzhlcE9GNkhVUGJqckhOb1o4YjBjRW5aNURBaGdRLzgreEpwTDI3TXBNcEVBeXVzVTAKUjlPVEhXKzhRTnVndEEyTWxKcU5UR2FScUlRcGhPNDRNYk1RMS9CVVdDUXBOODg5b3RaaEt6NWt1TEhqcWNUcQowbEoyL2NKVnhTV1V1N2RaQ0Q0SUtIQzU5VkRaY3AxNTdPOHRib1lCeUtuOUMzMjF5WXg5MWV3Z2dUaWRBK1dPCkZUZXZUOFUwVXNid29yWXd3T0dLbU9OemxybGhqZzVSWWdEYjJudGlEWjJ3bXoyUEpCR3dEbGZjVzJmWHFBYjQKSE5zNmoyRVE0M3BlRnVaMkpMN2RSK3V0REZLVlU0dW0zT3RHaVMrSHdJR2FSUkVKNW5BaFF1cm8xMU5wVk1XcgpwRTAvRmxzUmpMSW1BTVVBUUZ1R2xhNlNZRGJaQWdNQkFBR2pXVEJYTUE0R0ExVWREd0VCL3dRRUF3SUNwREFQCkJnTlZIUk1CQWY4RUJUQURBUUgvTUIwR0ExVWREZ1FXQkJSa0VRajVsTTNENGMwVnBlYm5SbHc4OWM2TEV6QVYKQmdOVkhSRUVEakFNZ2dwcmRXSmxjbTVsZEdWek1BMEdDU3FHU0liM0RRRUJDd1VBQTRJQkFRQ0lzQzBYMHZlbwoyZ2ZMYjBnYzR2TFlQaVd2TFVSc2xiSDc2Sk4wQUlRRVFldWg5SWl1ODBLdDBnb052cTNXUnhDckczckQyOHM5CnRsU2xjbWVsWVBrVThXV3dxVkRCRlNtZEZ0ZFlucDU1WHNSTHZGWmdOZm1RNlVrR2J5dzFyN0pVVE9xQTRxeHQKN21LdFViTGVxenM0dzlWTFJ3SmdGN2tMU2pGR09nU1RIMCs3alJja3ZDc2dwMDFMREtIellubjdzQnZ3WExZKworVnI2ME01VFhvd1RmVHJjTG9icnlZQzlkRks3L1dIVU94SjFNNEs0bDJ5aVZLdUVQK2tqeFVQRlZUNGppSmQ3CkRCRVhvOFRYLzByY21PT3p2KzRiRlkrRDZYYnY5Vm5FU2U5cHBiUkxmOXFkaGRDR1oxZFVBakh5c2Y2NHVRNy8KRHVFRUxNekFPNjlCCi0tLS0tRU5EIENFUlRJRklDQVRFLS0tLS0K
    server: https://172.18.0.4:6443
  name: kind-kind
contexts:
- context:
    cluster: kind-kind
    user: kind-kind
  name: kind-kind
- context:
    cluster: kind
    namespace: default
    user: mysql-sa
  name: restricted-context
current-context: kind-kind
kind: Config
preferences: {{}}
users:
- name: kind-kind
  user:
    client-certificate-data: LS0tLS1CRUdJTiBDRVJUSUZJQ0FURS0tLS0tCk1JSURLVENDQWhHZ0F3SUJBZ0lJUzJ6Qi83YzZ5MEV3RFFZSktvWklodmNOQVFFTEJRQXdGVEVUTUJFR0ExVUUKQXhNS2EzVmlaWEp1WlhSbGN6QWVGdzB5TkRBNU1qSXhNelV3TWpCYUZ3MHlOVEE1TWpJeE16VTFNakphTUR3eApIekFkQmdOVkJBb1RGbXQxWW1WaFpHMDZZMngxYzNSbGNpMWhaRzFwYm5NeEdUQVhCZ05WQkFNVEVHdDFZbVZ5CmJtVjBaWE10WVdSdGFXNHdnZ0VpTUEwR0NTcUdTSWIzRFFFQkFRVUFBNElCRHdBd2dnRUtBb0lCQVFDckZoSU0KeGFqanVaVFFkT0FyVFBhT1grYkFkWkJPb3c0UEhoRG1sS2tveUsxWEE0YkpxNGYwZ1E4dS9icUFnQ0Ixd1NzbApmSm9GUjJ2NWYrU2wrUnZYWUd4OVlJWTRieHdjaTJwQmpnK1k3V2RiWE5KM0ZOeG8vbWwwV2tVMUxDK1ZsS0ZGClhYemE5czI4MTgxZEFCOFhHSmpXUDhCUjBiM29FYW5ZUEt5RjZTU3hqeTQxZDd5d1FIbEJPTVVMLzdCRlU5RXUKN3VHcmZHMlNrZVVjZlFZTnc0eVhWc2k5Qy94elliTHhFNTlpeHRrTEN3SjVKak1CZGlPejUyYi8zZzc2VkVTYgpIWktxNFZOTjV2d1F1UzlyckhFMFlJL2VCTjd6NXhZbjJZTXpDNDdETlUzZkVLK3N5THhTeG9ubTVtaXRTcWR3CjM5Y1lxUE9LMEFXVERaSVJBZ01CQUFHalZqQlVNQTRHQTFVZER3RUIvd1FFQXdJRm9EQVRCZ05WSFNVRUREQUsKQmdnckJnRUZCUWNEQWpBTUJnTlZIUk1CQWY4RUFqQUFNQjhHQTFVZEl3UVlNQmFBRkdRUkNQbVV6Y1BoelJXbAo1dWRHWER6MXpvc1RNQTBHQ1NxR1NJYjNEUUVCQ3dVQUE0SUJBUUJXUnIvY0RTYXF1dTNrdktXZXpWNHROODlCCkNSOTJmZUpOcDVWOVlKY1dSYU5jQk1pUjFRMVNjMk9yMWJaVUZGSjFFb2duaFgwN3ZMdHdYQmZ5NFFGb1B1RDEKeVZpRWs3MGFOQVNPVThSbUFMV1RqWXo4QzJUWFl2c0x4aHBWVjkyZ3pubWxTd21Rckxmd1JtR09BaEwvZnJ0awp5RnQxazFkT2pneXJNVEhPblNZdVp6Z1IrbzRFQ2l6UEFkb0ZwU1YzY1RDR091YkhERlRoMmpzS1EzNDQyWUZQCjMySmFTV0pBdWd3NVNNRDBrYTg1YWdkZGhma1crakJYY1BGMENUbkdRa2N5QWhsTzN3dk4vdFFPWXFDb2NWcjgKTys4QWd1SUxTRFpQcjBtenR5TmlrOUxUTE5OZ3ZGWTk1RnEvTUJYYTJVUGY0Tm5KQWN1T3BLRE5pT3pkCi0tLS0tRU5EIENFUlRJRklDQVRFLS0tLS0K
    client-key-data: LS0tLS1CRUdJTiBSU0EgUFJJVkFURSBLRVktLS0tLQpNSUlFb2dJQkFBS0NBUUVBcXhZU0RNV280N21VMEhUZ0swejJqbC9td0hXUVRxTU9EeDRRNXBTcEtNaXRWd09HCnlhdUg5SUVQTHYyNmdJQWdkY0VySlh5YUJVZHIrWC9rcGZrYjEyQnNmV0NHT0c4Y0hJdHFRWTRQbU8xblcxelMKZHhUY2FQNXBkRnBGTlN3dmxaU2hSVjE4MnZiTnZOZk5YUUFmRnhpWTFqL0FVZEc5NkJHcDJEeXNoZWtrc1k4dQpOWGU4c0VCNVFUakZDLyt3UlZQUkx1N2hxM3h0a3BIbEhIMEdEY09NbDFiSXZRdjhjMkd5OFJPZllzYlpDd3NDCmVTWXpBWFlqcytkbS85NE8rbFJFbXgyU3F1RlRUZWI4RUxrdmE2eHhOR0NQM2dUZTgrY1dKOW1ETXd1T3d6Vk4KM3hDdnJNaThVc2FKNXVab3JVcW5jTi9YR0tqeml0QUZrdzJTRVFJREFRQUJBb0lCQUJHeVg3MlllSWJOdkhudgpqUHlOb25kSnJqbThMMmdpNzZKYXJzN2JFOEJYT2E3bGUzekMxSFpUSHpueUh1ZUoyVkcwNEh5cExkbGI4T3hHCjhXVEZwcjZaaDc5VVM2M3N1RkN2anhjbTFiQXc1bDhKOCs5RFppVXFJOGhZU2c1YytyTVRRN2RFRzFVZThGc1gKUzNQU1BtVUtNMHorSFN1WmNYWmUxVjI3c1BETTZIOURsOEVQYTNXdTlFUkFmelZqb1c1S1RYVTQrT3l5WndTOAplNHl0T0k0ajdPN1U4ZkZUcXlLL2cwVnkxM3gwVXhVSnJ2YUVBUS8wYmhYVGRUemdqcXcyMWl3VUc2REFUc3BWCjNLRFlyYnYvQ3BwbnhORC9zRlJkSHNVSEpKaGJvenNhVWo5bktwcUEzTGo2Nk92Q1JNQStlSUlySlA1R1J3VGgKeVFZRHBVMENnWUVBd0hxdjRMZDBFaWMzbThNdDh5VDBRUUJvU2MwdXplS2xiQUx2NHdib3FqdHQvckR4cy8zTAo4V0dtYTFYL1FxTGNMTTgvb1VRSTlUNk44L0dWakdqSkFkY0RDMDFoUSt0dDdmdTRBdDNiWHNtbUpKYmVhRDVBClJJR1ZXMER0U3RNYWN4TjdreitLRUFXODNoTFRmZW56aFkxR1VsT2NCNmM4bUV3SVRhU2dyKzhDZ1lFQTQ0d0cKcHRxdUNVZk5GbEdrSDRMZEd2dlIwajlVMHFlWWNVTER5N3lBOEh2TXFINnBvWEc4YTFuVjhLemNxZEJ0TTVwSgp2S25oZWk5TzA2VE9TR1R3bHE2U0RLdVJWL2V1N2J5bkJvcFF5SkJTYUlGNVJaNERBNmQ1T2RIM21lL3RDNUkyCkVsSWg2Rnd1WUNtdXhobWFzSlB4YkJhWUJHamc0bEhsWGRXejNmOENnWUFFT3EzaW9pVkt3TkhYK2xIb0pjZTQKSmVva3RQMXlTS2laMXZhdVpsaDJaUmZsb0wydTFzVEVhUURmR3VTZzhqTWtTT2w5QWFHd3djOGNyUkk4STVGSApHUkpZRFRzMTR0Wm5oRUJtejdraVBBd0tnY1loUkR6bFJIT2pyYW1KRzFwWmJQUXFLQnRBZnQvSGdXSmtRZCszCjc0SzhERnBCVU10a0RVZWhiUnlhd1FLQmdCMklmUXlHOFhPdTZBVnZqemV2eW5iSUhGR0hlc0RrazdxUGljNFYKcHo2UE10N2pvYXlja0hIMmRQZ0oxNUlLeFVHZlV0YXp6ZG9IN2RrMldMZTRzaWs4ZXlROTJGMXNmajNJOEh5Kwowd0ZWQ2YwYVlOMFNSeDNnVExHZWVONTM3M0pEQmRXVzUyTzdJeUhFQnpVYSthTFZjTTR3bUlacC9sWWhmdjJRCjBRbU5Bb0dBR1R5U1VPbmhTYVViL01zTHB4UFBKSWd0RDh3Yk5hSUlFTlowMjd0ZnIvOGk4LzJMczNZSmU4cG4KMDhZWTVqcXNXU2s4MHFTYzVBYTlaUm9KZXV3N2tSYVRaeEtjcjR5YXRGSGkxczdJYlB4bFZUS0hwdzRIUVk1YQo3RzZrTFk1MjVPRmwxdDZ0YVQ3V1dVY1ExTjFYM2V0Wmk4Uzh4ekpMYk9TeFdLWCtpcjg9Ci0tLS0tRU5EIFJTQSBQUklWQVRFIEtFWS0tLS0tCg==
- name: mysql-sa
  user:
    token: fd37f5ac83f3e112d74fe507ad64327a99ecebe5551d0e3ffc22303adc6780f0
"""

        # Write kubeconfig to a file
        #with open("/tmp/kubeconfig", "w") as f:
        #    f.write(kubeconfig)

        # Set the KUBECONFIG environment variable
        #os.environ["KUBECONFIG"] = "/tmp/kubeconfig"

        # Run kubectl set image command
        command = [
            "kubectl",
            "set",
            "image",
            f"deployment/{DEPLOYMENT_NAME}",
            f"{CONTAINER_NAME}={NEW_IMAGE}"
        ]

        result = subprocess.run(command, capture_output=True, text=True)

        if result.returncode == 0:
            return f"Deployment updated successfully: {result.stdout}"
        else:
            return f"Failed to update deployment: {result.stderr}"

    except Exception as e:
        return f"Error updating EKS deployment: {e}"


def lambda_handler(event, context):
    # Generate blog using Bedrock
    generate_blog = blog_generate_using_bedrock()

    if generate_blog:
        send_to_slack(generate_blog)

    # Update EKS deployment
    update_result = update_eks_deployment()
    send_to_slack(update_result)

    return {
        'statusCode': 200,
        'body': json.dumps('Blog Generation and EKS Deployment Update completed')
    }



