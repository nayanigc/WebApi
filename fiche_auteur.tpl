<!DOCTYPE html>
 <!-- page.tpl --> 
 <html lang="fr"> 
    <head>
        <meta http-equiv="Content-type" content="text/html; charset=utf-8">
        <link rel="stylesheet" type="text/css" media="screen" charset="utf-8" />
        <title>DBSP</title>
    </head>
    <body> 
          <h2> {{nom}}   {{prenom}} </h2>
          <center> nombre des journaux :  {{x}}  <a href='/authors/Journals/Synthese/{{nom}}/{{prenom}}'> Journal </a>  </center>
          <center> nombre des conference :  {{y}}  <a href='/authors/Conference/Synthese/{{nom}}/{{prenom}}'> Conference</a> </center>
          <center> nombre des co-Auteur :  {{z}}  <a href='/authors/Coauthors/synthese/{{nom}}/{{prenom}}'> Co-auteur </a> </center>
      </body>
</html>