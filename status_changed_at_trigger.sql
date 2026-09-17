-- Agrega un campo que solo se actualiza cuando cambia service_status o
-- report_status en service_control (no con cualquier otra edición), para
-- poder detectar registros "estancados" en el mismo estado.

ALTER TABLE service_control
  ADD COLUMN status_changed_at DATETIME NULL;

-- Backfill: para los registros ya existentes usamos created_at como punto
-- de partida (es lo más razonable que tenemos hasta ahora).
UPDATE service_control SET status_changed_at = created_at;

DROP TRIGGER IF EXISTS trg_service_control_status_changed;

DELIMITER $$
CREATE TRIGGER trg_service_control_status_changed
BEFORE UPDATE ON service_control
FOR EACH ROW
BEGIN
  IF NEW.service_status <> OLD.service_status OR NEW.report_status <> OLD.report_status THEN
    SET NEW.status_changed_at = NOW();
  END IF;
END$$
DELIMITER ;
