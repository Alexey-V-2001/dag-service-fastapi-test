if [[ -z "$VIRTUAL_ENV" ]]; then
    if [[ -d "venv" ]]; then
        echo "Virtual environment found. Activating..."
        source venv/bin/activate

        if [[ -z "$VIRTUAL_ENV" ]]; then
            echo "Failed to activate virtual environment."
            exit 1
        fi
    else
        echo "Virtual environment not found. Creating..."
        python -m venv venv

        echo "Activating..."
        source venv/bin/activate

        if [[ -z "$VIRTUAL_ENV" ]]; then
            echo "Failed to activate virtual environment after creation."
            exit 1
        fi
    fi
else
    echo "Virtual environment already activated."
fi

if [ ! -f "alembic.ini" ]; then
    cp alembic.ini.example alembic.ini
    echo "File alembic.ini was missing, created from alembic.ini.example"
fi

if alembic current | grep -q "(head)"; then
  echo "The database is already on the last migration."
else
  echo "Unapplied migrations found. Upgrading..."
  alembic upgrade head
fi

if ! pip freeze | grep -q -f requirements.txt; then
    echo "Installing python-packages..."
    pip install --no-cache-dir -r requirements.txt -I
fi

if [[ "$START" == "1" ]]; then
    echo "Running API..."
    python -m app.main
elif [[ "$START" == "2" ]]; then
    echo "Running tests only..."
    pytest tests/
elif [[ "$START" == "3" ]]; then
    echo "Running tests + code coverage report for app..."
    pytest --cov=app tests/
fi

echo "Deactivating..."
deactivate
