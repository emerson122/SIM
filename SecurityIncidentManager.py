import requests
import json
from datetime import datetime
import logging

class SecurityToolConnector:
    """
    Conector personalizado para integrar con una herramienta de seguridad 
    """
    
    def __init__(self, api_key: str, base_url: str):
        self.api_key = api_key
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        })
        
        # Configuración de logging
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)

    def get_alerts(self, start_time: datetime, end_time: datetime) -> list:
        """
        Obtiene alertas de seguridad en un rango de tiempo específico
        """
        try:
            endpoint = f"{self.base_url}/api/v1/alerts"
            params = {
                'start_time': start_time.isoformat(),
                'end_time': end_time.isoformat()
            }
            
            response = self.session.get(endpoint, params=params)
            response.raise_for_status()
            
            alerts = response.json()
            self.logger.info(f"Retrieved {len(alerts)} alerts successfully")
            return alerts
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error retrieving alerts: {str(e)}")
            raise

    def create_incident(self, alert_data: dict) -> str:
        """
        Crea un incidente basado en datos de alerta
        """
        try:
            endpoint = f"{self.base_url}/api/v1/incidents"
            
            incident_data = {
                'title': alert_data.get('title'),
                'severity': alert_data.get('severity'),
                'source': alert_data.get('source'),
                'description': alert_data.get('description'),
                'created_at': datetime.now().isoformat()
            }
            
            response = self.session.post(endpoint, json=incident_data)
            response.raise_for_status()
            
            incident_id = response.json().get('incident_id')
            self.logger.info(f"Created incident with ID: {incident_id}")
            return incident_id
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error creating incident: {str(e)}")
            raise

    def update_incident_status(self, incident_id: str, status: str) -> bool:
        """
        Actualiza el estado de un incidente
        """
        try:
            endpoint = f"{self.base_url}/api/v1/incidents/{incident_id}/status"
            
            data = {'status': status}
            response = self.session.put(endpoint, json=data)
            response.raise_for_status()
            
            self.logger.info(f"Updated incident {incident_id} status to {status}")
            return True
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error updating incident status: {str(e)}")
            raise

# Ejemplo de uso
if __name__ == "__main__":
    connector = SecurityToolConnector(
        api_key="your-api-key",
        base_url="https://security-tool-api.example.com"
    )
    
    # Obtener alertas recientes
    start_time = datetime(2024, 1, 1)
    end_time = datetime(2024, 1, 2)
    alerts = connector.get_alerts(start_time, end_time)
    
    # Crear incidente para cada alerta crítica
    for alert in alerts:
        if alert.get('severity') == 'critical':
            incident_id = connector.create_incident(alert)
            # Actualizar estado
            connector.update_incident_status(incident_id, "in_progress")