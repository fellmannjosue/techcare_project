INSERT INTO citas_billingue_grade_bl (id, name)
VALUES
(1, 'Kinder'),
(2, 'Prepa1'),
(3, 'Prepa 2'),
(4, 'Primero 1'),
(5, 'Primero 2'),
(6, 'Segundo 1'),
(7, 'Segundo 2'),
(8, 'Tercero 1');


-- estos no
SET FOREIGN_KEY_CHECKS = 0;

TRUNCATE TABLE tbl_spn_godfather;
TRUNCATE TABLE tbl_spn_sponsored;
TRUNCATE TABLE tbl_spn_sponsors;

SET FOREIGN_KEY_CHECKS = 1;
-- no


-- 🚫 Desactivar las restricciones de claves foráneas
SET FOREIGN_KEY_CHECKS = 0;

-- 🧹 Truncar las tablas (borrar todos los datos, reinicia auto_increment)
TRUNCATE TABLE citas_colegio_subject_col;
TRUNCATE TABLE citas_colegio_teacher_col;

-- ✅ Volver a activar las restricciones de claves foráneas
SET FOREIGN_KEY_CHECKS = 1;
