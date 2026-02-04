WITH consolidado_por_periodo AS (
    SELECT 
        cnpj, 
        raz, 
        ano, 
        tri, 
        SUM(val) as val_total
    FROM despesas
    WHERE val > 0  
    GROUP BY cnpj, raz, ano, tri
),
periodos AS (
    SELECT MIN(ano || tri) as inicio, MAX(ano || tri) as fim FROM consolidado_por_periodo
),
primeiro_tri AS (
    SELECT cnpj, raz, val_total as valor_inicial
    FROM consolidado_por_periodo
    WHERE (ano || tri) = (SELECT inicio FROM periodos)
),
ultimo_tri AS (
    SELECT cnpj, val_total as valor_final
    FROM consolidado_por_periodo
    WHERE (ano || tri) = (SELECT fim FROM periodos)
)

SELECT 
    p.raz, 
    p.cnpj,
    p.valor_inicial,
    u.valor_final,
    ((u.valor_final - p.valor_inicial) / NULLIF(p.valor_inicial, 0)) * 100 as crescimento_perc
FROM primeiro_tri p
JOIN ultimo_tri u ON p.cnpj = u.cnpj
WHERE p.valor_inicial > 1000 
ORDER BY crescimento_perc DESC
LIMIT 5;

SELECT 
    uf, 
    SUM(val) as despesa_total,
    AVG(val) as media_por_operadora,
    COUNT(DISTINCT cnpj) as total_operadoras
FROM despesas
GROUP BY uf
ORDER BY despesa_total DESC
LIMIT 5;

WITH media_geral AS (
    SELECT AVG(val) as valor_medio FROM despesas
),
operadoras_acima AS (
    SELECT cnpj, tri, ano
    FROM despesas, media_geral
    WHERE despesas.val > media_geral.valor_medio
)

SELECT COUNT(*) as total_operadoras_criticas
FROM (
    SELECT cnpj
    FROM operadoras_acima
    GROUP BY cnpj
    HAVING COUNT(*) >= 2
) as resultado;

