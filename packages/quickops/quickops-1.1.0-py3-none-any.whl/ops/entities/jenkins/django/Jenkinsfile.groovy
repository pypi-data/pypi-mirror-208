pipeline {
    agent {
    node {
      label '$params.agentLabel'
    }
  }

     parameters {
        string(name: 'agentLabel', defaultValue: '<>', description: 'Agent label')

        string(name: 'dockerCredentialsId', defaultValue: '<>', description: 'Docker registry credentials')

        string(name: 'dockerRegistryUrl', defaultValue: '<>', description: 'Docker registry address')

        string(name: 'image', defaultValue: '<>', description: 'Docker image name')

        string(name: 'version', defaultValue: '<>', description: 'Docker image version')

        string(name: 'email', defaultValue: '<>', description: 'Email to send message')

    }

    stages {
        stage("Code Checkout from repository") {
	    	steps {
				git branch: '$params.gitBranch',
					credentialsId: '$params.gitCredentialsId',
					url: '$params.gitRepositoryUrl'
			}
		}

        stage ('Update Python Modules') {
            steps {
                sh 'pip install --upgrade -r requirements.txt'
            }
        }

        stage ('Test') {
            steps {
                sh 'python ./manage.py runtests'
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
