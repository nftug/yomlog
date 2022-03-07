<template>
  <v-card v-bind="$attrs" class="pa-2">
    <v-card-title :class="titleClass" primary-title>{{ appName }} 利用規約</v-card-title>

    <v-card-text>
      <div class="mb-5">
        <div class="subtitle-1 my-3 font-weight-bold">第1条</div>
        <p>
          本サービスにおいては，登録希望者が本規約に同意の上，当社の定める方法によって利用登録を申請し，当社がこれを承認することによって，利用登録が完了するものとします。
          <br />
          当社は，利用登録の申請者に以下の事由があると判断した場合，利用登録の申請を承認しないことがあり，その理由については一切の開示義務を負わないものとします。

          <ul class="my-3">
            <li>利用登録の申請に際して虚偽の事項を届け出た場合</li>
            <li>本規約に違反したことがある者からの申請である場合</li>
            <li>その他，当社が利用登録を相当でないと判断した場合</li>
          </ul>
        </p>
      </div>

      <div class="my-5">
        <div class="subtitle-1 my-3 font-weight-bold">第2条</div>
        <p>
          ユーザーは，自己の責任において，本サービスのユーザーIDおよびパスワードを適切に管理するものとします。
          <br />
          ユーザーは，いかなる場合にも，ユーザーIDおよびパスワードを第三者に譲渡または貸与し，もしくは第三者と共用することはできません。当社は，ユーザーIDとパスワードの組み合わせが登録情報と一致してログインされた場合には，そのユーザーIDを登録しているユーザー自身による利用とみなします。
          <br />
          ユーザーID及びパスワードが第三者によって使用されたことによって生じた損害は，当社に故意又は重大な過失がある場合を除き，当社は一切の責任を負わないものとします。
        </p>
      </div>

      <div class="my-5">
        <div class="subtitle-1 my-3 font-weight-bold">第3条</div>
        <p>
          ユーザーは，本サービスの利用にあたり，以下の行為をしてはなりません。
          <ul class="my-3">
            <li>法令または公序良俗に違反する行為 犯罪行為に関連する行為</li>
            <li>当社のサービスの運営を妨害するおそれのある行為</li>
            <li>
              本サービスの他のユーザーまたはその他の第三者に不利益，損害，不快感を与える行為
            </li>
            <li>その他，当社が不適切と判断する行為</li>
          </ul>
        </p>
      </div>

      <div class="my-5">
        <div class="subtitle-1 my-3 font-weight-bold">第4条</div>
        <p>
          当社は，以下のいずれかの事由があると判断した場合，ユーザーに事前に通知することなく本サービスの全部または一部の提供を停止または中断することができるものとします。
          <ul class="my-3">
            <li>
              本サービスにかかるコンピュータシステムの保守点検または更新を行う場合
            </li>
            <li>
              地震，落雷，火災，停電または天災などの不可抗力により，本サービスの提供が困難となった場合
            </li>
            <li>コンピュータまたは通信回線等が事故により停止した場合</li>
            <li>その他，当社が本サービスの提供が困難と判断した場合</li>
          </ul>
        </p>
      </div>

      <div class="my-5">
        <div class="subtitle-1 my-3 font-weight-bold">第5条</div>
        <div>
          当社は，本サービスの提供の停止または中断により，ユーザーまたは第三者が被ったいかなる不利益または損害についても，一切の責任を負わないものとします。
        </div>
      </div>

      <div class="my-5">
        <div class="subtitle-1 my-3 font-weight-bold">第6条</div>
        <p>
          当社は，ユーザーが以下のいずれかに該当する場合には，事前の通知なく，ユーザーに対して，本サービスの全部もしくは一部の利用を制限し，またはユーザーとしての登録を抹消することができるものとします。
          <ul class="my-3">
            <li>本規約のいずれかの条項に違反した場合</li>
            <li>当社からの連絡に対し，一定期間返答がない場合</li>
            <li>その他，当社が本サービスの利用を適当でないと判断した場合</li>
          </ul>
          当社は，本条に基づき当社が行った行為によりユーザーに生じた損害について，一切の責任を負いません。
        </p>
      </div>

      <div class="my-5">
        <div class="subtitle-1 my-3 font-weight-bold">第7条</div>
        <p>
          ユーザーは，当社の定める退会手続により，本サービスから退会できるものとします。
        </p>
      </div>

      <div class="my-5">
        <div class="subtitle-1 my-3 font-weight-bold">第8条</div>
        <p>
          当社は，ユーザーへの事前の告知なしに本サービスの内容を変更、追加または廃止することがあり、ユーザーはこれを承諾するものとします。
        </p>
      </div>

      <div class="my-5">
        <div class="subtitle-1 my-3 font-weight-bold">第9条</div>
        <p>
          当社は，本サービスの利用によって取得する個人情報については，当社「プライバシーポリシー」に従い適切に取り扱うものとします。
        </p>
      </div>
    </v-card-text>
  </v-card>
</template>

<script>
import Mixins from '@/mixins'

export default {
  mixins: [Mixins],
  props: {
    titleClass: {type: String, default: 'text-h5'  }
  }
}
</script>

<style scoped>
br {
display: block;
content: "";
padding: 2px 0;
}
</style>
