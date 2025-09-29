"""
Airflow pool configuration for ETL pipeline resource management.
"""

from airflow.models import Pool
from airflow import settings


def create_airflow_pools():
    """
    Create Airflow pools for resource management in ETL pipeline.
    
    Pools help manage concurrent task execution and prevent resource contention.
    """
    session = settings.Session()
    
    # Define pools with their configurations
    pools_config = [
        {
            'pool': 'ingestion_pool',
            'slots': 3,
            'description': 'Pool for parallel data ingestion tasks (API, files, DB replication)'
        },
        {
            'pool': 'transformation_pool', 
            'slots': 2,
            'description': 'Pool for dbt transformation tasks'
        },
        {
            'pool': 'validation_pool',
            'slots': 2,
            'description': 'Pool for data quality validation tasks'
        },
        {
            'pool': 'monitoring_pool',
            'slots': 1,
            'description': 'Pool for monitoring and alerting tasks'
        },
        {
            'pool': 'heavy_compute_pool',
            'slots': 1,
            'description': 'Pool for compute-intensive tasks (large aggregations, ML)'
        },
        {
            'pool': 'external_api_pool',
            'slots': 5,
            'description': 'Pool for external API calls with rate limiting'
        }
    ]
    
    try:
        for pool_config in pools_config:
            # Check if pool already exists
            existing_pool = session.query(Pool).filter(
                Pool.pool == pool_config['pool']
            ).first()
            
            if existing_pool:
                # Update existing pool
                existing_pool.slots = pool_config['slots']
                existing_pool.description = pool_config['description']
                print(f"Updated pool: {pool_config['pool']}")
            else:
                # Create new pool
                new_pool = Pool(
                    pool=pool_config['pool'],
                    slots=pool_config['slots'],
                    description=pool_config['description']
                )
                session.add(new_pool)
                print(f"Created pool: {pool_config['pool']}")
        
        session.commit()
        print("Pool configuration completed successfully")
        
    except Exception as e:
        session.rollback()
        print(f"Error configuring pools: {e}")
        raise
    finally:
        session.close()


def list_airflow_pools():
    """
    List all configured Airflow pools.
    
    Returns:
        List of pool configurations
    """
    session = settings.Session()
    
    try:
        pools = session.query(Pool).all()
        
        pool_info = []
        for pool in pools:
            pool_info.append({
                'pool': pool.pool,
                'slots': pool.slots,
                'description': pool.description,
                'occupied_slots': pool.occupied_slots(),
                'running_slots': pool.running_slots(),
                'queued_slots': pool.queued_slots()
            })
        
        return pool_info
        
    except Exception as e:
        print(f"Error listing pools: {e}")
        return []
    finally:
        session.close()


def get_pool_utilization():
    """
    Get current pool utilization metrics.
    
    Returns:
        Dictionary with pool utilization statistics
    """
    session = settings.Session()
    
    try:
        pools = session.query(Pool).all()
        
        utilization_stats = {
            'total_pools': len(pools),
            'total_slots': 0,
            'occupied_slots': 0,
            'utilization_rate': 0.0,
            'pool_details': []
        }
        
        for pool in pools:
            total_slots = pool.slots
            occupied = pool.occupied_slots()
            running = pool.running_slots()
            queued = pool.queued_slots()
            
            pool_utilization = occupied / total_slots if total_slots > 0 else 0
            
            utilization_stats['total_slots'] += total_slots
            utilization_stats['occupied_slots'] += occupied
            
            utilization_stats['pool_details'].append({
                'pool_name': pool.pool,
                'total_slots': total_slots,
                'occupied_slots': occupied,
                'running_slots': running,
                'queued_slots': queued,
                'utilization_rate': pool_utilization,
                'status': 'high_utilization' if pool_utilization > 0.8 else 'normal'
            })
        
        # Calculate overall utilization
        if utilization_stats['total_slots'] > 0:
            utilization_stats['utilization_rate'] = (
                utilization_stats['occupied_slots'] / utilization_stats['total_slots']
            )
        
        return utilization_stats
        
    except Exception as e:
        print(f"Error getting pool utilization: {e}")
        return {}
    finally:
        session.close()


if __name__ == "__main__":
    # Run pool setup
    create_airflow_pools()
    
    # Display current pools
    pools = list_airflow_pools()
    print("\nConfigured Airflow Pools:")
    print("-" * 50)
    for pool in pools:
        print(f"Pool: {pool['pool']}")
        print(f"  Slots: {pool['slots']}")
        print(f"  Description: {pool['description']}")
        print(f"  Occupied: {pool['occupied_slots']}")
        print(f"  Running: {pool['running_slots']}")
        print(f"  Queued: {pool['queued_slots']}")
        print()
    
    # Display utilization
    utilization = get_pool_utilization()
    print("Pool Utilization Summary:")
    print("-" * 50)
    print(f"Total Pools: {utilization.get('total_pools', 0)}")
    print(f"Total Slots: {utilization.get('total_slots', 0)}")
    print(f"Occupied Slots: {utilization.get('occupied_slots', 0)}")
    print(f"Overall Utilization: {utilization.get('utilization_rate', 0):.2%}")
