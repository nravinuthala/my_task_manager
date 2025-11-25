pipeline {
    agent any
    
    environment {
        PYTHON_VERSION = '3.11'
        APP_NAME = 'task-management-microservice'
        REGISTRY = 'docker.io'
        IMAGE_TAG = "${BUILD_NUMBER}"
    }
    
    stages {
        stage('Checkout') {
            steps {
                script {
                    echo '====== Checking out code from repository ======'
                    checkout scm
                    echo 'Code checkout completed successfully'
                }
            }
        }
        
        stage('Build') {
            steps {
                script {
                    echo '====== Building the application ======'
                    
                    // Install dependencies
                    sh '''
                        echo 'Installing Python dependencies...'
                        python -m pip install --upgrade pip
                        pip install -r requirements.txt
                        echo 'Dependencies installed successfully'
                    '''
                    
                    // Build Docker image (optional)
                    sh '''
                        echo 'Docker image build can be added here'
                    '''
                }
            }
        }
        
        stage('Test') {
            steps {
                script {
                    echo '====== Running tests ======'
                    
                    sh '''
                        echo 'Starting application server in background...'
                        python myapp.py > /tmp/app.log 2>&1 &
                        APP_PID=$!
                        echo $APP_PID > /tmp/app.pid
                        
                        echo 'Waiting for server to start...'
                        sleep 3
                        
                        echo 'Running test suite...'
                        pip install requests
                        python test_api.py
                        
                        echo 'Stopping application server...'
                        kill $APP_PID || true
                        
                        echo 'Tests completed successfully'
                    '''
                }
            }
        }
        
        stage('Deploy') {
            when {
                branch 'main'
            }
            steps {
                script {
                    echo '====== Deploying application ======'
                    
                    sh '''
                        echo 'Deploying to production environment...'
                        
                        # Example deployment steps
                        echo 'Application deployment steps:'
                        echo '1. Copy application files to deployment server'
                        echo '2. Install dependencies on deployment server'
                        echo '3. Start/restart the application service'
                        echo '4. Verify application health'
                        
                        echo 'Deployment completed successfully'
                    '''
                }
            }
        }
    }
    
    post {
        always {
            script {
                echo '====== Post-build actions ======'
                
                // Clean up any running processes
                sh '''
                    if [ -f /tmp/app.pid ]; then
                        kill $(cat /tmp/app.pid) || true
                        rm /tmp/app.pid
                    fi
                '''
                
                // Archive test results/logs if they exist
                sh '''
                    echo 'Archiving logs and artifacts...'
                    # Add artifact archiving commands here if needed
                '''
            }
        }
        
        success {
            script {
                echo '====== Build Successful ======'
                // Add notification (email, Slack, etc.)
                echo 'Pipeline execution completed successfully'
            }
        }
        
        failure {
            script {
                echo '====== Build Failed ======'
                // Add notification (email, Slack, etc.)
                echo 'Pipeline execution failed. Check logs for details.'
            }
        }
    }
}
