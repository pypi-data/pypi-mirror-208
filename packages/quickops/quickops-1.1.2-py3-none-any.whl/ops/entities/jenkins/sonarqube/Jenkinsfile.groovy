pipeline {
agent {
    node {
      label '$params.agentLabel'
    }
  }
  parameters {
        string(name: 'agentLabel', defaultValue: '<>', description: 'Agent label')

        string(name: 'gitBranch', defaultValue: '<>', description: 'Repository branch to clone')

        string(name: 'gitCredentialsId', defaultValue: '<>', description: 'Git access token')

        string(name: 'gitRepositoryUrl', defaultValue: '<>', description: 'Git repository address')

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

   stage('Code Quality Check via SonarQube') {
    	steps {
       		script {
       			def scannerHome = tool 'sonarqube';
           		withSonarQubeEnv("sonarqube-container") {
           			sh "${tool("sonarqube")}/bin/sonar-scanner \
           			-Dsonar.projectKey=<project_key> \
           			-Dsonar.sources=. \
           			-Dsonar.host.url=<sonar host> \
           			-Dsonar.login=<sonar login>"
            	}
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