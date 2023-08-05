pipeline {

	agent {
		node {
			label '$params.agentLabel'
		}
	}

	tools {
		nodejs "node"
	}

	parameters {
		string(name: 'agentLabel', defaultValue: '<>', description: 'Agent label')

		string(name: 'email', defaultValue: '<>', description: 'Email to send message')

		string(name: 'gitBranch', defaultValue: '<>', description: 'Repository branch to clone')

		string(name: 'gitCredentialsId', defaultValue: '<>', description: 'Git access token')

		string(name: 'gitRepositoryUrl', defaultValue: '<>', description: 'Git repository address')

	}

	stages {

		stage("Code Checkout from repository") {
			steps {
				git branch: '$params.gitBranch',
					credentialsId: '$params.gitCredentialsId',
					url: '$params.gitRepositoryUrl'
			}
		}

		stage('Build') {
			steps {
				sh 'npm install'
				sh 'npm run build'
			}
		}

		stage('Test') {
			steps {
				sh 'npm run test'
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

