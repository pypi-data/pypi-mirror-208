<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:xs="http://www.w3.org/2001/XMLSchema" xmlns:fn="http://www.w3.org/2005/xpath-functions" xmlns:BCE="www.sat.gob.mx/esquemas/ContabilidadE/1_1/BalanzaComprobacion" xmlns:BCEB="http://www.sat.gob.mx/esquemas/ContabilidadE/1_1/BalanzaComprobacion" version="2.0"><xsl:include href="../../../utilerias.xslt"/><xsl:output method="text" version="1.0" encoding="UTF-8" indent="no"/><xsl:template match="/">|<xsl:apply-templates select="/BCE:Balanza"/><xsl:apply-templates select="/BCEB:Balanza"/>||</xsl:template><xsl:template match="BCE:Balanza"><xsl:call-template name="Requerido"><xsl:with-param name="valor" select="./@Version"/></xsl:call-template><xsl:call-template name="Requerido"><xsl:with-param name="valor" select="./@RFC"/></xsl:call-template><xsl:call-template name="Requerido"><xsl:with-param name="valor" select="./@Mes"/></xsl:call-template><xsl:call-template name="Requerido"><xsl:with-param name="valor" select="./@Anio"/></xsl:call-template><xsl:call-template name="Requerido"><xsl:with-param name="valor" select="./@TipoEnvio"/></xsl:call-template><xsl:call-template name="Opcional"><xsl:with-param name="valor" select="./@FechaModBal"/></xsl:call-template><xsl:apply-templates select="./BCE:Ctas"/></xsl:template><xsl:template match="BCE:Ctas"><xsl:call-template name="Requerido"><xsl:with-param name="valor" select="./@NumCta"/></xsl:call-template><xsl:call-template name="Requerido"><xsl:with-param name="valor" select="./@SaldoIni"/></xsl:call-template><xsl:call-template name="Requerido"><xsl:with-param name="valor" select="./@Debe"/></xsl:call-template><xsl:call-template name="Requerido"><xsl:with-param name="valor" select="./@Haber"/></xsl:call-template><xsl:call-template name="Requerido"><xsl:with-param name="valor" select="./@SaldoFin"/></xsl:call-template></xsl:template><xsl:template match="BCEB:Balanza"><xsl:call-template name="Requerido"><xsl:with-param name="valor" select="./@Version"/></xsl:call-template><xsl:call-template name="Requerido"><xsl:with-param name="valor" select="./@RFC"/></xsl:call-template><xsl:call-template name="Requerido"><xsl:with-param name="valor" select="./@Mes"/></xsl:call-template><xsl:call-template name="Requerido"><xsl:with-param name="valor" select="./@Anio"/></xsl:call-template><xsl:call-template name="Requerido"><xsl:with-param name="valor" select="./@TipoEnvio"/></xsl:call-template><xsl:call-template name="Opcional"><xsl:with-param name="valor" select="./@FechaModBal"/></xsl:call-template><xsl:apply-templates select="./BCEB:Ctas"/></xsl:template><xsl:template match="BCEB:Ctas"><xsl:call-template name="Requerido"><xsl:with-param name="valor" select="./@NumCta"/></xsl:call-template><xsl:call-template name="Requerido"><xsl:with-param name="valor" select="./@SaldoIni"/></xsl:call-template><xsl:call-template name="Requerido"><xsl:with-param name="valor" select="./@Debe"/></xsl:call-template><xsl:call-template name="Requerido"><xsl:with-param name="valor" select="./@Haber"/></xsl:call-template><xsl:call-template name="Requerido"><xsl:with-param name="valor" select="./@SaldoFin"/></xsl:call-template></xsl:template></xsl:stylesheet>