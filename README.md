# CRM Performance Backend

A high-performance Django backend designed to handle large-scale CRM data with efficient listing, searching, and filtering capabilities for ~3 million records.

## Features

- **Scalable Architecture**: Handles 3M+ records efficiently
- **Optimized Queries**: Uses Django ORM best practices for large datasets
- **Advanced Filtering**: Filter by any field across joined tables
- **Pagination**: Built-in pagination support
- **Caching**: Redis-backed response caching
- **Performance Metrics**: Detailed query timing information
- **Modern Stack**: Django + PostgreSQL + Redis + Docker

## Technology Stack

- **Backend**: Django 5.2 + Django REST Framework
- **Database**: PostgreSQL 15 (optimized for large datasets)
- **Cache**: Redis 7
- **Containerization**: Docker
- **Package Management**: Poetry
- **Monitoring**: Django Debug Toolbar (dev only)

## Performance Optimizations

1. **Database-Level Optimizations**:
   - `select_related` for foreign key relationships (Address)
   - `prefetch_related` with custom Prefetch for many-to-many relationships
   - Field-specific queries with `only()` to limit fetched columns
   - Query `distinct()` for complex joins with filtering
   - Proper database indexing

2. **Caching Strategy**:
   - Full response caching with Redis (10-minute TTL)
   - Cache keys based on full request paths
   - Cache invalidation on write operations

3. **Query Optimization**:
   - Dynamic filter building with validation
   - Configurable ordering
   - Pagination at database level

## Installation

### Prerequisites

- Docker and Docker Compose
- Python 3.13
- Poetry


### Setup

1. Clone the repository:
   ```bash
   git clone [https://github.com/karippery/crm-performance-backend.git]
   cd crm-performance-backend
   ```

2. Copy environment file and configure:
   ```bash
   cp .env.example .env
   # Edit .env as needed
   ```

3. Install dependencies:
   ```bash
   poetry install
   ```

4. Build and start containers:
   ```bash
   docker-compose -f docker-compose.dev.yml up --build
   ```

5. Apply migrations:
   ```bash
   docker-compose -f docker-compose.dev.yml exec web python manage.py migrate
   ```


## API Endpoints

### List AppUsers
`GET /api/v1/appusers/`

**Parameters**:
- `page`: Page number (default: 1)
- `page_size`: Items per page (default: 20)
- `ordering`: Field to order by (prefix with '-' for descending)
- `?first_name=`: filter 

**Response Includes**:
- Paginated list of AppUsers with related Address and CustomerRelationship data
- Performance metadata (query time, cache status, ...)

## Handling Large Datasets

The system employs several strategies to handle 3M+ records efficiently:

1. **Database Optimization**:
   - Properly indexed tables
   - Limited column selection

2. **Application-Level Optimization**:
   - Efficient serializer with minimal processing
   - Prefetch patterns to avoid N+1 queries
   - Chunked processing for batch operations

3. **Infrastructure**:
   - Dedicated PostgreSQL container with optimized configuration
   - Redis caching layer
   - Containerized environment for consistent performance

## Benchmarking

The system includes built-in performance metrics in API responses:

```json
// ... data ...
{
  "meta": {
    "query_time": 0.145,
    "response_time": 0.152,
    "cache_hit": false
  }
  
}
```


## Development

### Running Tests
```bash
docker-compose -f docker-compose.dev.yml exec web pytest
```



### Monitoring
- Django Debug Toolbar available in development at `/__debug__/`


## Future Improvements

1. Implement asynchronous task processing for data loading
2. Add more advanced caching strategies (time-based invalidation)
3. Implement database read replicas for scaling
4. Add query batching for complex operations
5. Implement rate limiting
6. Add more detailed analytics endpoints


