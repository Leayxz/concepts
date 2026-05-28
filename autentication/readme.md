# Autenticação
### Conceito
- Toda autenticação deve responder quem é o usuário, e fazer uma marcação de identificação. É necessário porque APIs stateless não guardam identidade, apenas recebem REQs.

- Por exemplo, um usuário envia email e senha para o sistema validar identidade e gerar uma marcação, se os dados estiverem corretos, o sistema gera uma autenticação e passa a confiar nela.

- Dessa maneira é possível controlar quem pode acessar o que, e evitar vulnerabilidades como acesso não autorizado e vazamento de dados.

- A autenticação pode ser feita de diferentes maneiras, mas a mais comum é usando um `Json Web Token (JWT)`, por ser stateless, melhor para distribuição e escalabilidade.

- O JWT funciona como um cartão de identificação, contendo principalmente um sub (Subject) e exp (Expiration), além de roles e permissions para autorização. O sub (Subject) deve ser algo estável, único e imutável, idealmente um uuid representando o usuário.

- O payload do JWT não é criptografado por padrão, apenas assinado, ou seja, pode ser lido facilmente, mas não pode ser alterado sem invalidar a assinatura. Isso significa que um Json Web Token não garante segurança, garante identidade válida, integridade e autenticidade vinda do servidor, ou seja, se um atacante roubar um JWT, ele terá acesso por tempo determinado, até a expiração do access token. Caso o refresh token seja roubado, ele terá acesso por um tempo muito maior.

### Como deve ser feito
- O registro dos usuários é feito utilizando criptografia hash para persistência das senhas de maneira segura, evitando engenharia reversa e vazamento de senhas. A autenticação de identidade é feita somente após a validação da senha, devolvendo um `access token` e um `refresh token`, somente se a senha estiver correta.

- O `access token` é responsável por manter o usuário autenticado por um breve momento, enquanto o `refresh token` possui uma duração de expiração maior. O access token é primeiramente gerado ao realizar login, enquanto o refresh token é responsável por gerar novos access tokens após a expiração do primário.

- Dessa maneira, o usuário não precisa ficar realizando login sempre que o access token primário expirar, e não gera vulnerabilidades para o sistema com um access token infinito. O refresh token possuí um tempo de expiração maior, porém, idealmente ele vive dentro do sistema, sendo possível revogar em casos de vulnerabilidade.

- A renovação do access token acontece geralmente em um endpoint, onde o client possa pedir por um novo access token, ou seja, é feito o decode do `refresh token`, com a expiração maior, e feito o encode para retorno de um novo `access token`, com expiração menor.

- O fluxo de cadastro seguiria como: `Email + Senha > Hash Senha > Persistência`. Enquanto o fluxo de login seguiria como: `Email + Senha > Validação da Senha Hash > Return Access e Refresh Token`.

- O fluxo de renovação do refresh token seguiria como: `Access Expirado > Endpoint Refresh > Refresh Válido > Novo Access Curto`. Caso o refresh token não seja válido, o usuário é jogado para login novamente.


# Autorização
### Conceito
- A autorização deve responder o que o usuário pode fazer e acessar. Por exemplo, sem autenticação o usuário não deve acessar outros endpoints, ou mesmo com autenticação válida, o usuário não pode acessar os dados que não pertencem à ele. Assim, baseado em identidade, o usuário deve conseguir editar seu próprio perfil, mas não o perfil do outro.

- A autorização existe para proteger recursos, limitar ações, isolar usuários e impedir abuso, evitando desastres através do controle de acesso.

### Como deve ser feito
- Rotas geralmente são protegidas através de `decorators`, como `@login_required`, ou manualmente, recebendo os dados através dos `headers` e realizando o `decode()` do access token. Se for válido, o usuário consegue acessar a rota e acessar seus dados. Se não for válido, ele não é permitido.

- O fluxo de autorização manual seguiria como: `Header Authorization > decode() > Sucesso | Falha`. Dessa maneira, se a validação falhar, o usuário não consegue acessar rotas ou dados indevidos.




# Observações
- Aparentemente é melhor utilizar `JSONResponse` em vez de controlar o retorno com dict `return {}`, devido ao controle dos status code.
