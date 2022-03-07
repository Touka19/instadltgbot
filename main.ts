import {
  GetAuthorizedFacebookPagesRequest,
  GetAuthorizedFacebookPagesResponse,
} from 'instagram-graph-api';

const request: GetAuthorizedFacebookPagesRequest =
  new GetAuthorizedFacebookPagesRequest('IGQVJXVS0xY0NuZAF9lSVVhWThlbnJhbjFoSnhpLTBHZA1hhTF9xLUJQcVpjV3VaVDVabktvak1JSnNpWVFRdy1lai1XaDM5SGZAmY3VyOTByYVRlcGhSa3ZATdFoxTnVIemtma1pISUR3TmVJejhaZADdiUAZDZD');

request.execute().then((response: GetAuthorizedFacebookPagesResponse) => {
    console.log(response);
  //const firstFacebookPage: string = response.getAuthorizedFacebookPages()[0].id;
  //console.log(firstFacebookPage);
});
