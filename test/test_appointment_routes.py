from datetime import datetime, timedelta
from fastapi.testclient import TestClient
from sqlmodel import Session
from test.mocks.mocked_clients import clients_data
from test.mocks.mocked_professionals import professionals_data
from test.mocks.mocked_services import services_data
from database.models import Client, Professional, Service, Appointment
from .utils import log_test

BASE_URL = "/appointments/"
NOW = datetime.now().replace(hour=14, minute=0, second=0, microsecond=0)
APPOINTMENT_DURATION = timedelta(minutes=30)

# Helper functions


def create_basic_entities(session: Session) -> tuple[Client, Professional, Service]:
    """Cria e retorna entidades básicas persistidas"""
    client = Client(**clients_data[0])
    client2 = Client(**clients_data[1])
    professional = Professional(**professionals_data[0])
    professional2 = Professional(**professionals_data[1])
    service = Service(**services_data[0])

    session.add_all([client, client2, professional, professional2, service])
    session.commit()
    return client, professional, service


def create_appointment(session: Session, start_time: datetime, professional_id: int = 1, client_id: int = 1) -> Appointment:
    """Cria um agendamento persistido"""
    end_time = start_time + APPOINTMENT_DURATION
    appointment = Appointment(
        client_id=client_id,
        professional_id=professional_id,
        service_id=1,
        start_time=start_time,
        end_time=end_time
    )
    session.add(appointment)
    session.commit()
    return appointment

# Test cases


class TestAppointmentBusinessRules:
    def test_create_appointment_professional_conflict_overlapping_start(self, client: TestClient, db_session: Session):
        """
        Testa criação onde novo agendamento começa 15min após um existente que ainda está em andamento
        Existente: 14:00-14:30
        Novo: 14:15-14:45 → Deve conflitar
        """
        # Configuração
        _, professional_ent, service_ent = create_basic_entities(
            db_session)
        existing_start = NOW.replace(minute=0)
        create_appointment(db_session, existing_start)

        # Novo agendamento
        new_start = existing_start + timedelta(minutes=15)
        payload = {
            "client_id": 2,
            "professional_id": professional_ent.id,
            "service_id": service_ent.id,
            "start_time": new_start.isoformat()
        }

        # Execução
        response = client.post(f"{BASE_URL}create/", json=payload)
        log_test(
            self.test_create_appointment_professional_conflict_overlapping_start.__name__,
            "response",
            response.json()
        )

        # Validação
        assert response.status_code == 409
        assert "professional" in response.json()["detail"].lower()

    def test_create_appointment_professional_conflict_overlapping_end(self, client: TestClient, db_session: Session):
        """
        Testa criação onde novo agendamento começa 15min antes de um existente
        Existente: 14:15-14:45
        Novo: 14:00-14:30 → Deve conflitar
        """
        _, professional_ent, service_ent = create_basic_entities(
            db_session)
        existing_start = NOW.replace(minute=15)
        create_appointment(db_session, existing_start)

        new_start = existing_start - timedelta(minutes=15)
        payload = {
            "client_id": 2,
            "professional_id": professional_ent.id,
            "service_id": service_ent.id,
            "start_time": new_start.isoformat()
        }

        response = client.post(f"{BASE_URL}create/", json=payload)
        log_test(
            self.test_create_appointment_professional_conflict_overlapping_end.__name__,
            "response",
            response.json()
        )

        assert response.status_code == 409
        assert "professional" in response.json()["detail"].lower()

    def test_update_appointment_professional_conflict_overlapping_start(self, client: TestClient, db_session: Session):
        """
        Testa atualização que causa conflito com agendamento existente do mesmo profissional
        Existente: 14:00-14:30
        Update: 14:15-14:45 → Deve falhar
        """
        create_basic_entities(db_session)

        # Cria dois agendamentos iniciais
        original_appointment = create_appointment(
            db_session, NOW.replace(minute=0))
        create_appointment(
            db_session, NOW.replace(minute=30), client_id=2)

        # Tenta mover o segundo para conflitar com o primeiro
        update_payload = {
            "start_time": NOW.replace(minute=15).isoformat(),
        }

        response = client.put(
            f"{BASE_URL}update/{original_appointment.id}",
            json=update_payload
        )
        log_test(
            self.test_update_appointment_professional_conflict_overlapping_start.__name__,
            "response",
            response.json()
        )

        assert response.status_code == 409
        assert "professional" in response.json()["detail"].lower()

    def test_update_appointment_professional_conflict_overlapping_end(self, client: TestClient, db_session: Session):
        """
        Testa atualização que causa conflito com agendamento existente do mesmo profissional
        Existente: 14:15-14:45
        Update: 14:00-14:30 → Deve falhar
        """
        create_basic_entities(db_session)

        create_appointment(db_session, NOW.replace(minute=30))
        appointment_to_update = create_appointment(
            db_session, NOW.replace(minute=0), client_id=2)

        update_payload = {
            "start_time": (NOW.replace(minute=45)).isoformat(),
        }

        response = client.put(
            f"{BASE_URL}update/{appointment_to_update.id}",
            json=update_payload
        )
        log_test(
            self.test_update_appointment_professional_conflict_overlapping_end.__name__,
            "response",
            response.json()
        )

        assert response.status_code == 409
        assert "professional" in response.json()["detail"].lower()

    def test_create_appointment_client_conflict_overlapping_start(self, client: TestClient, db_session: Session):
        """
        Testa criação onde novo agendamento do mesmo cliente começa durante um existente
        Existente: 14:00-14:30
        Novo: 14:15-14:45 → Deve conflitar
        """
        client_ent, _, service_ent = create_basic_entities(
            db_session)
        create_appointment(db_session, NOW.replace(minute=0))

        new_start = NOW.replace(minute=15)
        payload = {
            "client_id": client_ent.id,
            "professional_id": 2,  # Profissional diferente
            "service_id": service_ent.id,
            "start_time": new_start.isoformat()
        }

        response = client.post(f"{BASE_URL}create/", json=payload)
        log_test(
            self.test_create_appointment_client_conflict_overlapping_start.__name__,
            "response",
            response.json()
        )

        assert response.status_code == 409
        assert "client" in response.json()["detail"].lower()

    def test_create_appointment_client_conflict_overlapping_end(self, client: TestClient, db_session: Session):
        """
        Testa criação onde novo agendamento do mesmo cliente termina durante um existente
        Existente: 14:15-14:45
        Novo: 14:00-14:30 → Deve conflitar
        """
        client_ent, _, service_ent = create_basic_entities(
            db_session)
        create_appointment(db_session, NOW.replace(minute=15))

        payload = {
            "client_id": client_ent.id,
            "professional_id": 2,
            "service_id": service_ent.id,
            "start_time": NOW.replace(minute=0).isoformat()
        }

        response = client.post(f"{BASE_URL}create/", json=payload)
        log_test(
            self.test_create_appointment_client_conflict_overlapping_end.__name__,
            "response",
            response.json()
        )

        assert response.status_code == 409
        assert "client" in response.json()["detail"].lower()

    def test_update_appointment_client_conflict_overlapping_start(self, client: TestClient, db_session: Session):
        """
        Testa atualização que causa conflito de horário para o mesmo cliente
        Existente: 14:00-14:30
        Update: 14:15-14:45 → Deve falhar
        """
        create_basic_entities(db_session)

        # Cria dois agendamentos iniciais
        create_appointment(
            db_session,
            NOW.replace(minute=30),
            professional_id=2)
        appointment_to_update = create_appointment(
            db_session,
            NOW.replace(minute=0),
        )

        update_payload = {
            "start_time": (NOW.replace(minute=45)).isoformat()
        }

        response = client.put(
            f"{BASE_URL}update/{appointment_to_update.id}",
            json=update_payload
        )
        log_test(
            self.test_update_appointment_client_conflict_overlapping_start.__name__,
            "response",
            response.json()
        )

        assert response.status_code == 409
        assert "client" in response.json()["detail"].lower()

# Testes complementares


class TestEdgeCases:
    def test_appointment_creation_after(self, client: TestClient, db_session: Session):
        """
        Testa criação onde novo agendamento começa exatamente quando outro termina
        Existente: 14:00-14:30
        Novo: 14:30-15:00 → Deve permitir
        """
        client_ent, professional_ent, service_ent = create_basic_entities(
            db_session)
        create_appointment(db_session, NOW.replace(minute=0))

        payload = {
            "client_id": client_ent.id,
            "professional_id": professional_ent.id,
            "service_id": service_ent.id,
            "start_time": (NOW.replace(minute=30)).isoformat()
        }

        response = client.post(f"{BASE_URL}create/", json=payload)
        log_test(
            self.test_appointment_creation_after.__name__,
            "response",
            response.json()
        )

        assert response.status_code == 201

    def test_appointment_creation_before(self, client: TestClient, db_session: Session):
        """
        Teste onde novo agendamento começa antes de um outro
        Existente: 14:30-15:00
        Novo: 14:00-14:30 → Deve permitir
        """
        client_ent, professional_ent, service_ent = create_basic_entities(
            db_session)
        create_appointment(db_session, NOW.replace(minute=30))

        payload = {
            "client_id": client_ent.id,
            "professional_id": professional_ent.id,
            "service_id": service_ent.id,
            "start_time": (NOW.isoformat())
        }

        response = client.post(
            f"{BASE_URL}create/", json=payload)
        log_test(
            self.test_appointment_creation_before.__name__,
            "response",
            response.json()
        )

        assert response.status_code == 201

    def test_appointment_update_before(self, client: TestClient, db_session: Session):
        """
        Teste onde agendamento é reagendado exatamente antes de outro
        Existente: 14:30-15:00
        Outro: 14:00- 13:30
        Update para antes do outro: 13:30-14:00 → Deve permitir
        """
        client_ent, professional_ent, service_ent = create_basic_entities(
            db_session)
        appointment = create_appointment(db_session, NOW.replace(minute=30))
        create_appointment(db_session, NOW)  # another

        payload = {
            "client_id": client_ent.id,
            "professional_id": professional_ent.id,
            "service_id": service_ent.id,
            "start_time": (NOW.replace(hour=13, minute=30).isoformat())
        }

        response = client.put(
            f"{BASE_URL}update/{appointment.id}", json=payload)
        log_test(
            self.test_appointment_update_before.__name__,
            "response",
            response.json()
        )

        assert response.status_code == 200


class TestValidationRules:
    # def test_appointment_past_date(self, client: TestClient, db_session: Session):
    #     """
    #     Testa criação de agendamento no passado
    #     """
    #     client_ent, professional_ent, service_ent = create_basic_entities(
    #         db_session)

    #     payload = {
    #         "client_id": client_ent.id,
    #         "professional_id": professional_ent.id,
    #         "service_id": service_ent.id,
    #         "start_time": (NOW - timedelta(days=1)).isoformat()
    #     }

    #     response = client.post(f"{BASE_URL}create/", json=payload)
    #     assert response.status_code == 400
    #     assert "past" in response.json()["detail"].lower()

    def test_create_appointment_end_time_calculus(self, client: TestClient, db_session: Session):
        """
        Testa se o final do agendamento corresponde ao tempo estimado do serviço após criação
        'end_time' não é enviado e é calculado baseado no início + tempo do serviço
        """
        client_ent, professional_ent, service_ent = create_basic_entities(
            db_session)

        payload = {
            "client_id": client_ent.id,
            "professional_id": professional_ent.id,
            "service_id": service_ent.id,
            "start_time": NOW.isoformat(),
        }

        response = client.post(f"{BASE_URL}create/", json=payload)
        response_json = response.json()
        log_test(
            self.test_create_appointment_end_time_calculus.__name__,
            "response",
            response_json
        )

        assert response.is_success == True
        assert 'end_time' in response_json
        assert response_json['end_time'] == (
            NOW + timedelta(minutes=service_ent.estimated_time, microseconds=-1)).isoformat()

    def test_update_appointment_end_time_calculus(self, client: TestClient, db_session: Session):
        """
        Testa se o final do agendamento é atualizado quando o ínício é atualizado
        'end_time' não é enviado e é calculado baseado no início + tempo do serviço
        """
        create_basic_entities(db_session)
        # vou criar um serviço mais longo que 30min
        new_service = Service(**services_data[1])
        db_session.add(new_service)
        db_session.commit()
        # criado com servico id 1 (30 min)
        appointment = create_appointment(db_session, NOW)

        payload = {
            "service_id": new_service.id
        }

        response = client.put(
            f"{BASE_URL}update/{appointment.id}", json=payload)
        response_json = response.json()
        log_test(
            self.test_update_appointment_end_time_calculus.__name__,
            "response",
            response_json
        )

        assert response.is_success
        assert 'end_time' in response_json
        assert response_json['end_time'] == (
            NOW + timedelta(minutes=new_service.estimated_time, microseconds=-1)).isoformat()

    def test_create_invalid_date(self, client: TestClient, db_session: Session):
        """
        Testa passando duma string diferente de uma data no formato ISO no campo start_time
        """
        client_ent, professional_ent, service_ent = create_basic_entities(
            db_session)

        payload = {
            "client_id": client_ent.id,
            "professional_id": professional_ent.id,
            "service_id": service_ent.id,
            "start_time": str(NOW.timestamp()),
        }

        response = client.post(f"{BASE_URL}create/", json=payload)
        response_json = response.json()
        log_test(
            self.test_create_invalid_date.__name__,
            "response",
            response_json
        )
        assert "iso formated date" in response_json["detail"].lower()
