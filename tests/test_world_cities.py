import os
import sqlite3


def get_db_path():
    return os.path.join(os.path.dirname(__file__), '..', 'world_cities.db')


def test_cities_table_exists():
    """Verify that the cities table exists in the database."""
    db_path = get_db_path()
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()

    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='cities';")
    result = cursor.fetchone()
    assert result is not None, "Cities table does not exist"

    connection.close()


def test_cities_table_columns():
    """Verify the schema of the cities table."""
    db_path = get_db_path()
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()

    cursor.execute("PRAGMA table_info(cities);")
    columns = cursor.fetchall()

    assert len(columns) == 4, f"Expected 4 columns, found {len(columns)}"

    expected_names = ['id', 'name', 'population', 'country']
    actual_names = [column[1] for column in columns]
    assert actual_names == expected_names, (
        f"Column name mismatch: expected {expected_names}, got {actual_names}"
    )

    expected_types = {
        'id': 'INTEGER',
        'name': 'TEXT',
        'population': 'INTEGER',
        'country': 'TEXT',
    }

    for column in columns:
        name = column[1]
        actual_type = (column[2] or '').upper()
        if name in expected_types:
            assert actual_type in {expected_types[name], 'INT'}, (
                f"Column type mismatch for {name}: expected {expected_types[name]}, got {actual_type}"
            )

        if name == 'id':
            assert column[5] == 1, f"Primary key mismatch for id: expected 1, got {column[5]}"

    connection.close()


def test_beijing_population_update():
    """Test that Beijing's population was updated correctly."""
    db_path = get_db_path()
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()
    cursor.execute("SELECT population FROM cities WHERE name = 'Beijing'")
    row = cursor.fetchone()
    assert row is not None, "Beijing row not found"
    assert int(row[0]) == 19400000  # Updated population value


def test_deleted_cities():
    """Test that specified cities were deleted."""
    db_path = get_db_path()
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()
    cursor.execute("SELECT name FROM cities WHERE name IN ('New York', 'Cairo', 'Paris')")
    deleted_cities = cursor.fetchall()
    assert len(deleted_cities) == 0


def test_final_cities_count():
    """Test that all initial cities were inserted correctly."""
    db_path = get_db_path()
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()
    cursor.execute("SELECT COUNT(*) FROM cities")
    count = cursor.fetchone()[0]
    assert count == 7  # After DELETE operations


def test_remaining_cities():
    """Test the data integrity of remaining cities."""
    db_path = get_db_path()
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()
    cursor.execute("SELECT name, population, country FROM cities ORDER BY name")
    cities = cursor.fetchall()

    normalized_cities = [
        (name, int(population), country) for name, population, country in cities
    ]

    expected_cities = [
        ('Beijing', 19400000, 'China'),
        ('Lagos', 14368332, 'Nigeria'),
        ('Mumbai', 12442373, 'India'),
        ('Osaka', 2752123, 'Japan'),
        ('Sao Paulo', 12252023, 'Brazil'),
        ('Sydney', 5312163, 'Australia'),
        ('Tokyo', 13515271, 'Japan'),
    ]

    assert normalized_cities == expected_cities