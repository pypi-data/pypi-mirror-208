pipeline {
    agent any

    triggers{
        bitbucketPush()
    }

     parameters {
        string(name: 'dockerCredentialsId', defaultValue: '<>', description: 'Docker registry credentials')

        string(name: 'dockerRegistryUrl', defaultValue: '<>', description: 'Docker registry address')

        string(name: 'image', defaultValue: '<>', description: 'Docker image name')

        string(name: 'version', defaultValue: '<>', description: 'Docker image version')

        string(name: 'email', defaultValue: '<>', description: 'Email to send message')
     }

    stages {
        stage ('Test & Build Artifact') {
            agent {
                docker {
                    image 'openjdk:11'
                    args '-v "$PWD":/app'
                    reuseNode true
                }
            }
            steps {
                sh './gradlew clean build'
            }
        }
        stage ('Build & Push docker image') {
            steps {
                withDockerRegistry(credentialsId: '$params.dockerCredentialsId', url: '$params.dockerRegistryUrl') {
                    sh "
                    docker build -t ${params.image} . && \
                    docker tag ${params.image} ${image}:${params.version} && \
                    docker push ${params.image}:${params.version}
                    "
                }
            }
        }
    }

    post {
		always {
			mail to: '$params.email',
				subject: "${currentBuild.fullDisplayName} ${currentBuild.result}",
				body: "Check out ${env.BUILD_URL}"
		}
	}
}