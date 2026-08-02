from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse
from Middleware.jwt_bearer import JWTBearer
from Config.db import get_db
from Models.service_control_model import ServiceControlModel
from Models.client_model import ClientModel
from Models.client_lines_model import ClientLinesModel
from sqlalchemy.orm import Session
import anthropic
import json
import os

ai_router = APIRouter()


@ai_router.post('/ai/report-assistant', tags=["AI"], dependencies=[Depends(JWTBearer(required_roles=[1, 2]))])
def report_assistant(request: Request):
    data = getattr(request.state, "json_data", {})
    notes = data.get("notes", "").strip()
    equipment = data.get("equipment_name", "")
    services = data.get("service_types", "")
    report_type = data.get("report_type", "standard")

    if not notes:
        return JSONResponse(
            status_code=400,
            content={"status": 400, "message": "Se requieren las notas del técnico", "data": None}
        )

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        return JSONResponse(
            status_code=500,
            content={"status": 500, "message": "ANTHROPIC_API_KEY no está configurada en el servidor", "data": None}
        )

    context_lines = []
    if equipment:
        context_lines.append(f"Equipo intervenido: {equipment}")
    if services:
        context_lines.append(f"Tipo de servicio: {services}")
    context_lines.append(f"Notas del técnico: {notes}")
    context = "\n".join(context_lines)

    is_acesco = report_type == "acesco"

    if is_acesco:
        json_structure = '{"service_description": "...", "information": "...", "conclusions": "...", "recommendations": "..."}'
        fields_hint = "descripción del servicio, información técnica, conclusiones y recomendaciones"
    else:
        json_structure = '{"service_description": "...", "information": "..."}'
        fields_hint = "descripción del servicio e información técnica"

    prompt = f"""Eres un redactor técnico de Mega Hydraulic S.A.S., empresa de mantenimiento hidráulico industrial.

Con base en las siguientes notas del técnico, redacta el texto formal y profesional para el reporte de servicio ({fields_hint}).

{context}

Responde ÚNICAMENTE con un JSON válido con esta estructura exacta:
{json_structure}

Reglas:
- Lenguaje técnico formal en español
- Sé específico según las notas proporcionadas
- Las conclusiones deben indicar el estado final del equipo tras la intervención
- Las recomendaciones deben ser preventivas y concretas
- No incluyas ningún texto fuera del JSON"""

    try:
        client = anthropic.Anthropic(api_key=api_key)
        with client.messages.stream(
            model="claude-haiku-4-5",
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}],
        ) as stream:
            message = stream.get_final_message()

        text = next(
            (block.text for block in message.content if hasattr(block, "text")),
            ""
        ).strip()

        if text.startswith("```"):
            parts = text.split("```")
            text = parts[1] if len(parts) > 1 else text
            if text.startswith("json"):
                text = text[4:]
        text = text.strip()

        result = json.loads(text)
        return JSONResponse(content={"status": 200, "message": "OK", "data": result})

    except json.JSONDecodeError:
        return JSONResponse(
            status_code=500,
            content={"status": 500, "message": "Error al procesar la respuesta de IA", "data": None}
        )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"status": 500, "message": f"Error al generar texto: {str(e)}", "data": None}
        )


@ai_router.post('/ai/service-query', tags=["AI"], dependencies=[Depends(JWTBearer(required_roles=[1, 2]))])
def service_query(request: Request, db: Session = Depends(get_db)):
    data = getattr(request.state, "json_data", {})
    question = data.get("question", "").strip()

    if not question:
        return JSONResponse(
            status_code=400,
            content={"status": 400, "message": "Se requiere la pregunta", "data": None}
        )

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        return JSONResponse(
            status_code=500,
            content={"status": 500, "message": "ANTHROPIC_API_KEY no está configurada", "data": None}
        )

    service_status_map = {0: "Por aprobar", 1: "En ejecución", 2: "Por facturar", 3: "Facturado"}
    report_status_map = {0: "Por hacer", 1: "Por enviar", 2: "Enviado"}
    component_map = {0: "Hidráulico", 1: "Suministro", 2: "Mecánico"}

    records = db.query(
        ServiceControlModel.id,
        ServiceControlModel.activity_date,
        ServiceControlModel.value,
        ServiceControlModel.service_status,
        ServiceControlModel.report_status,
        ServiceControlModel.component,
        ServiceControlModel.invoice,
        ServiceControlModel.invoice_date,
        ServiceControlModel.solped,
        ServiceControlModel.hes,
        ServiceControlModel.consecutive,
        ClientModel.name.label('client_name'),
        ClientLinesModel.name.label('client_line'),
    ).outerjoin(
        ClientModel, ServiceControlModel.client_id == ClientModel.id
    ).outerjoin(
        ClientLinesModel, ServiceControlModel.client_line_id == ClientLinesModel.id
    ).filter(
        ServiceControlModel.status == 1
    ).order_by(
        ServiceControlModel.activity_date.desc()
    ).all()

    records_list = [
        {
            "id": r.id,
            "fecha": str(r.activity_date),
            "cliente": r.client_name,
            "linea": r.client_line,
            "componente": component_map.get(r.component, "N/A"),
            "valor": float(r.value) if r.value else 0,
            "estado": service_status_map.get(r.service_status, "N/A"),
            "estado_reporte": report_status_map.get(r.report_status, "N/A"),
            "factura": r.invoice,
            "fecha_factura": str(r.invoice_date) if r.invoice_date else None,
            "solped": r.solped,
            "hes": r.hes,
        }
        for r in records
    ]

    context = json.dumps(records_list, ensure_ascii=False, default=str)

    prompt = f"""Eres un asistente de análisis de datos para Mega Hydraulic S.A.S., empresa de mantenimiento hidráulico industrial.

Tienes acceso a los registros del Control de Servicio. Cada registro tiene:
- fecha: fecha de la actividad
- cliente: nombre del cliente
- linea: línea del cliente
- componente: Hidráulico, Suministro o Mecánico
- valor: valor del servicio en pesos colombianos
- estado: Por aprobar | En ejecución | Por facturar | Facturado
- estado_reporte: Por hacer | Por enviar | Enviado
- factura: número de factura (null si no tiene)
- fecha_factura: fecha de facturación
- solped / hes: documentos de compra

Datos actuales ({len(records_list)} registros activos):
{context}

Pregunta: {question}

Responde de forma clara y concisa en español. Usa formato de pesos colombianos para valores monetarios (ej: $1.200.000). Si la pregunta no puede responderse con los datos disponibles, indícalo."""

    try:
        client = anthropic.Anthropic(api_key=api_key)
        with client.messages.stream(
            model="claude-haiku-4-5",
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}],
        ) as stream:
            message = stream.get_final_message()

        answer = next(
            (block.text for block in message.content if hasattr(block, "text")),
            ""
        ).strip()

        return JSONResponse(content={"status": 200, "message": "OK", "data": {"answer": answer}})

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"status": 500, "message": f"Error al procesar la consulta: {str(e)}", "data": None}
        )
