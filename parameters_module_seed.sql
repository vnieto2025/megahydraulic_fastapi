INSERT INTO modules (name, description, icon, action, status) VALUES
  ('PARÁMETROS', 'GESTIÓN DE CATALOGOS: mano de obra, herramientas, actividades, componentes, estados, etc.', 'configuraciones.png', '/parameters', 1);

INSERT INTO permission (type_user_id, module_id, status)
VALUES (1, LAST_INSERT_ID(), 1);
