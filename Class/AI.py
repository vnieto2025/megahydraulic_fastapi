import json
import os
from Utils.tools import Tools, CustomException
from Models.ai_agent_config_model import AIAgentConfigModel


class AI:

    def __init__(self, db):
        self.tools = Tools()
        self.db = db

    def _assert_agent_active(self):
        active = self.db.query(AIAgentConfigModel).filter(
            AIAgentConfigModel.status == 1
        ).first()
        if not active:
            raise CustomException("El asistente de IA está desactivado actualmente.", 403)

    def report_assistant(self, data: dict):
        self._assert_agent_active()

        notes = (data.get("notes") or "").strip()
        if not notes:
            raise CustomException("Se requieren las notas del técnico.")

        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise CustomException("OPENAI_API_KEY no está configurada en el servidor.")

        equipment = data.get("equipment_name") or ""
        services = data.get("service_types") or ""
        report_type = data.get("report_type", "standard")
        is_acesco = report_type == "acesco"
        is_service_control = report_type == "service_control"

        context_lines = []
        if equipment:
            context_lines.append(f"Equipo/zona de trabajo: {equipment}")
        if services:
            context_lines.append(f"Tipo de servicio: {services}")
        context_lines.append(f"Notas del técnico: {notes}")
        context = "\n".join(context_lines)

        if is_acesco:
            json_structure = '{"service_description": "...", "information": "...", "conclusions": "...", "recommendations": "..."}'
            fields_hint = "descripción del servicio, información técnica, conclusiones y recomendaciones"
        elif is_service_control:
            json_structure = '{"service_description": "...", "information": "...", "note": "..."}'
            fields_hint = "descripción del servicio, información técnica y una nota breve"
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
            from openai import OpenAI
            client = OpenAI(api_key=api_key)
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"},
            )
            text = response.choices[0].message.content.strip()
            result = json.loads(text)
        except json.JSONDecodeError:
            raise CustomException("Error al procesar la respuesta de IA.")
        except CustomException:
            raise
        except Exception as ex:
            raise CustomException(f"Error al generar texto con IA: {str(ex)}")

        return self.tools.output(200, "Ok.", result)
