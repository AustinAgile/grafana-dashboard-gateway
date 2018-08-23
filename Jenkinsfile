@Library("PipelineUtilities@feature/CONDEL-1497-create-initial-pbr-5-deployment") _

String cloud = "EKS"
String buildNamespace = "jenkinsdevcondel"
String appVersion = "0.1.${env.BUILD_NUMBER}"
def args = [:]

String label = "jenkins-${UUID.randomUUID().toString()}"
podTemplate(cloud: "${cloud}", label: label, namespace: "${buildNamespace}",
        containers: [
            containerTemplate(name: 'jnlp', image: 'artifactory.mattersight.local:6002/jenkins/kubejenkinsagent:latest', alwaysPullImage: false, args: '${computer.jnlpmac} ${computer.name}'),
            containerTemplate(name: 'docker', image: 'artifactory.mattersight.local:6002/jenkins/mattersightdocker:latest', alwaysPullImage: false, command:'cat', ttyEnabled:true)
        ],
        volumes: [hostPathVolume(hostPath: '/var/run/docker.sock', mountPath: '/var/run/docker.sock')]) {
    node(label) {
        stage("checkout") {
            checkout scm
        }
//        container("docker") {
//            stage("docker build") {
//                dir("_docker") {
//                    String registry = "artifactory.mattersight.local:6002"
//                    String repoImagePath = "condel"
//                    String repoName = scm.getUserRemoteConfigs()[0].getUrl().tokenize('/').last().split("\\.")[0].toLowerCase()
//                    withCredentials([usernamePassword(credentialsId: "Artifactory", usernameVariable: 'USERNAME', passwordVariable: 'PASSWORD')]) {
//                        sh "docker login -u ${'$USERNAME'} -p ${'$PASSWORD'} ${registry}"
//                        sh "docker build --network=host --tag ${registry}/${repoImagePath}${repoName}:${appVersion} ."
//                        sh "docker push ${registry}/${repoImagePath}${repoName}:${appVersion}"
//                        sh "docker tag ${registry}/${repoImagePath}${repoName}:${appVersion} ${registry}/${repoImagePath}${repoName}:latest"
//                        sh "docker push ${registry}/${repoImagePath}${repoName}:latest"
//                    }
//                }
//            }
//        }
        container("jnlp") {
            stage("helm build") {
                withCredentials([file(credentialsId: 'JenkinsEKSUserKubeConfig', variable: 'FILE'), file(credentialsId: 'JenkinsAWSProfileCreds', variable: 'FILE2')]) {
                    withEnv(["KUBECONFIG=${FILE}", "AWS_SHARED_CREDENTIALS_FILE=${FILE2}"]) {
                        sh "helm init --client-only"
                        sh "kubectl port-forward \$(kubectl get pods --namespace chartmuseum -l \"app=chartmuseum\" -l \"release=chartmuseum\" -o jsonpath=\"{.items[0].metadata.name}\") 8080:8080 --namespace chartmuseum &"
                        def charts = findFiles(glob: "*helm/**/Chart.yaml")
                        if (charts.size() > 0) {
                            def chart = readYaml(file: charts[0].path)
                            properties.name = chart.name
                            properties.chartVersion = properties.chartVersion ?: args.chartVersion ?: chart.version
                            properties.appVersion = appVersion ?: properties.appVersion ?: chart.appVersion
                        } else {
                            throw new Exception("Chart.yaml not found")
                        }

                        properties.filePath = charts[0].path.replaceAll("Chart.yaml", "")

                        def reqFiles = findFiles(glob: "${properties.filePath}/requirements.*")
                        if (reqFiles.size() > 0) {
                            def req = readYaml(file: reqFiles[0].path)
                            req.dependencies.eachWithIndex { app, i ->
                                def repoPath = app.repository.replaceAll("\\.", "/").replaceAll("alias:", "http://127.0.0.1:8080/")
                                def aliasName = app.repository.replaceAll("alias:", "")
                                sh "helm repo add ${aliasName} ${repoPath}"
                            }
                        } else {
                            println("Requirements file not found")
                        }
                        //    if(properties.uploadFeaturesToSnapshot) {
                        //        properties.chartRepoRelativePath = properties.chartRepoRelativePath.replaceAll(properties.chartRepoRelativePath.split("/")[2],"snapshot")
                        //        properties.doUpload = true
                        //    }
                        if (properties.onlyUploadOnMasterRelease) {
                            boolean isUploadable = false
                            switch (env.BRANCH_NAME) {
                                case "master":
                                case ~/release.*/:
                                    isUploadable = true
                                    break
                                default:
                                    break
                            }
                            properties.doUpload = isUploadable
                        }
                        sh "helm dependency build ${properties.filePath}"
                        if (properties.options == null) {
                            properties.options = ""
                        }
                        sh "helm package ${properties.filePath} --version ${properties.chartVersion} --app-version ${properties.appVersion} ${properties.options}"
                        if (properties.doUpload) {
                            if (properties.force) {
                                sh "curl -X \"DELETE\" http://127.0.0.1:8080/api/${properties.chartRepoRelativePath}/charts/${properties.name}/${properties.chartVersion}"
                            }
                            sh "curl --data-binary \"@${properties.name}-${properties.chartVersion}.tgz\" http://127.0.0.1:8080/api/${properties.chartRepoRelativePath}/charts"
                        } else {
                            println("Skipping upload")
                        }
                    }
                }
            }
        }
    }
}