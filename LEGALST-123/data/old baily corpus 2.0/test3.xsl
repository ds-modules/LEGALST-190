<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
  <xsl:output indent="yes" method="xml"/>
  <xsl:strip-space elements="*"/>

  <xsl:template match="/p">
    <data>
      <defendantName><xsl:value-of select="normalize-space(descendant::persName[@type='defendantName'])"/></defendantName>
      <defendantGender><xsl:value-of select="descendant::persName[@type='defendantName']/interp[@type='gender']/@value"/></defendantGender>
      <offenceCategory><xsl:value-of select="descendant::interp[@type='offenceCategory']/@value"/></offenceCategory>
      <offenceSubCategory><xsl:value-of select="descendant::interp[@type='offenceSubcategory']/@value"/></offenceSubCategory>

      <victimName><xsl:value-of select="normalize-space(descendant::persName[@type='victimName'])"/></victimName>
      <victimGender><xsl:value-of select="descendant::persName[@type='victimName']/interp[@type='gender']/@value"/></victimGender>
      <verdictCategory><xsl:value-of select="descendant::interp[@type='verdictCategory']/@value"/></verdictCategory>
      <verdictSubCategory><xsl:value-of select="descendant::interp[@type='verdictSubcategory']/@value"/></verdictSubCategory>
      <punishmentCategory><xsl:value-of select="descendant::interp[@type='punishmentCategory']/@value"/></punishmentCategory>

      <trialText><xsl:value-of select="normalize-space(/p)"/></trialText>
    </data>
  </xsl:template> 

</xsl:stylesheet>