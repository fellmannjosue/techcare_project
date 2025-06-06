-- Desactivar comprobación de claves foráneas (MySQL)
SET FOREIGN_KEY_CHECKS = 0;

-- TRUNCATE TABLE `sponsors2`.`citas_colegio_appointment_col`;
TRUNCATE TABLE `sponsors2`.`enfermeria_atencionmedica`;
-- TRUNCATE TABLE `sponsors2`.`enfermeria_grado`;
TRUNCATE TABLE `sponsors2`.`enfermeria_inventariomedicamento`;
-- TRUNCATE TABLE `sponsors2`.`enfermeria_medico`;
-- TRUNCATE TABLE `sponsors2`.`enfermeria_proveedor`;
-- TRUNCATE TABLE `sponsors2`.`enfermeria_responsable`;
TRUNCATE TABLE `sponsors2`.`enfermeria_usomedicamento`;
-- TRUNCATE TABLE `sponsors2`.`inventario_computadora`;
-- TRUNCATE TABLE `sponsors2`.`inventario_datashow`;
-- TRUNCATE TABLE `sponsors2`.`inventario_impresora`;
-- TRUNCATE TABLE `sponsors2`.`inventario_inventoryitem`;
-- TRUNCATE TABLE `sponsors2`.`inventario_televisor`;
-- TRUNCATE TABLE `sponsors2`.`maintenance_record`;
-- TRUNCATE TABLE `sponsors2`.`tipo_falla`;
-- TRUNCATE TABLE `sponsors2`.`tickets`;
-- TRUNCATE TABLE `sponsors2`.`citas_billingue_appointment_bl`;

-- Restaurar comprobación de claves foráneas
SET FOREIGN_KEY_CHECKS = 1;


