pipeline {
  agent {
    node {
      label 'docker'
    }
  }

   triggers{
        bitbucketPush()
    }

  options {
    timestamps()
  }

  environment {
    IMAGE = readMavenPom().getArtifactId()
    VERSION = readMavenPom().getVersion()
  }

   parameters {
        string(name: 'email', defaultValue: '<>', description: 'Email to send message')

        string(name: 'image', defaultValue: '<>', description: 'Docker image name')

        string(name: 'version', defaultValue: '<>', description: 'Docker image version')

    }

  stages {
    stage('Build') {
      agent {
        docker {
          reuseNode true
          image 'maven:3.5.0-jdk-8'
        }
      }
      steps {
        withMaven(options: [findbugsPublisher(), junitPublisher(ignoreAttachments: false)]) {
          sh 'mvn clean install'
        }
      }
      post {
        success {
          archiveArtifacts(artifacts: '**/target/*.jar', allowEmptyArchive: true)
        }
      }
    }

        stage('Sonar Scan') {
          agent {
            docker {
              reuseNode true
              image 'maven:3.5.0-jdk-8'
            }
          }
          environment {
            SONAR = credentials('sonar')
          }
          steps {
            sh 'mvn sonar:sonar -Dsonar.login=$SONAR_PSW'
          }
        }

    stage('Build and Publish Image') {
      when {
        branch 'master'
      }
      steps {
        sh "
          docker build -t ${params.image} . && \
          docker tag ${params.image} ${params.image}:${params.version} && \
          docker push ${params.image}:${params.version}
          "
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