pipeline {
    agent any

    stages {

        stage('Checkout') {
            steps {
                git branch: 'main', url: 'https://github.com/seela-2001/blog-app-with-DRF'
            }
        }

        stage('Load .env from credentials') {
            steps {
                script {
                    // Expect a Jenkins Secret File credential with ID: blog-app-env
                    withCredentials([file(credentialsId: 'blog-app-env', variable: 'ENV_FILE')]) {
                        sh '''
                        set -e
                        echo "Loading .env file ..."
                        cp "$ENV_FILE" ./.env
                        # Show which keys are present (names only)
                        grep -E '^[A-Za-z_][A-Za-z0-9_]*=' ./.env | cut -d= -f1 | sed 's/^/ENV: /'
                        '''
                    }
                }
            }
        }

        stage('Build images') {
            steps {
                sh '''
                set -e
                echo "Building docker images ..."
                docker compose build
                '''
            }
        }

        stage('Start database') {
            steps {
                sh '''
                set -e
                echo "Starting database ..."
                docker compose up -d db
                # Wait for postgres to be ready
                docker compose exec -T db sh -c 'for i in $(seq 1 30); do pg_isready -U "$POSTGRES_USER" && exit 0; sleep 2; done; exit 1'
                '''
            }
        }

        stage('Run migrations') {
            steps {
                sh '''
                set -e
                echo "Running migrations ..."
                docker compose run --rm web python manage.py migrate --noinput
                '''
            }
        }

        stage('Start services') {
            steps {
                sh '''
                set -e
                echo "Starting stack ..."
                docker compose up -d
                docker compose ps
                '''
            }
        }

    }

    post {
        success {
            echo 'The app is running'
        }
        failure {
            echo 'Something went wrong!'
        }
    }
}