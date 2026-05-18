#!/bin/bash

echo "📋 Container Logs"
echo "=================="
echo ""
echo "1. All logs"
echo "2. Backend only"
echo "3. Frontend only"
echo "4. Database only"
echo ""
read -p "Select option: " option

case $option in
    1)
        docker-compose logs -f
        ;;
    2)
        docker-compose logs -f backend
        ;;
    3)
        docker-compose logs -f frontend
        ;;
    4)
        docker-compose logs -f postgres
        ;;
    *)
        echo "Invalid option"
        exit 1
        ;;
esac
