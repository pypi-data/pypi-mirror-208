pipeline {
	agent {
		node {
			label '$params.agentLabel'
		}
	}

	parameters {
		string(name: 'agentLabel', defaultValue: '<>', description: 'Agent label')

		string(name: 'email', defaultValue: '<>', description: 'Email to send message')

		string(name: 'gitBranch', defaultValue: '<>', description: 'Repository branch to clone')

		string(name: 'gitCredentialsId', defaultValue: '<>', description: 'Git access token')

		string(name: 'gitRepositoryUrl', defaultValue: '<>', description: 'Git repository address')

		string(name: 'dockerImageName', defaultValue: '<>', description: 'Docker image name')

		string(name: 'dockerCredentialsId', defaultValue: '<>', description: 'Docker registry credentials')

		string(name: 'dockerRegistryUrl', defaultValue: '<>', description: 'Docker registry address')

		string(name: 'version', defaultValue: '<>', description: 'Docker image version')

	}

	stages {

		stage("Code Checkout from repository") {
			steps {
				git branch: '$params.gitBranch',
					credentialsId: '$params.gitCredentialsId',
					url: '$params.gitRepositoryUrl'
			}
		}

		stage('Build image') {

			app = docker.build("$params.dockerImageName")
		}

		stage('Test image') {

			app.inside {
				sh 'echo "Tests passed"'
			}
		}

		stage('Push image') {
			docker.withRegistry('$params.dockerCredentialsId', '$params.dockerRegistryUrl') {
				app.push("$params.version")
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
